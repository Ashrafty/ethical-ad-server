"""
List all payouts.

Example::

    # List all active payouts
    ./manage.py payouts

    # List all active payouts and show the email
    ./manage.py payouts --email
"""
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Context
from django.template import Template
from django.utils import timezone

from ...models import Publisher
from ...utils import generate_publisher_payout_data
from adserver.utils import generate_absolute_url

email_template = """
{% autoescape off %}
<p>
Thanks for being one of the first publishers on our EthicalAds network.
We do payouts by the 15th of the month,
as noted in our <a href="https://www.ethicalads.io/publisher-policy/">Publisher Policy</a>.
If you haven't had a chance to look it over, please do,
as it sets expectations around ad placements and payments.
</p>

{% if ctr < .07 %}

<p>
We generally expect all our publishers to maintain a CTR (click though rate) around or above .1%.
Your CTR is currently {{ report.total.ctr|floatformat:3 }}%,
which is below our current minimum.
We have a few suggestions in our <a href="https://www.ethicalads.io/publishers/faq/">FAQ</a> around improving placements,
but the main thing is just having the ad be on the screen in a visible place for long enough for users to see and click on it.

</p>

{% endif %}

<p>
We are now processing payments for <strong>{{ today|date:"F" }} {{ today|date:"Y" }}</strong>,
and you made a total of <strong>${{ report.total.revenue_share|floatformat:2 }}</strong> for ads displayed between <strong>{{ last_payout_date|date:"F j" }}-{{ last_day_last_month|date:"F j" }}</strong>.
You can find the full report for this billing cycle on our <a href="{{ report_url }}">revenue report</a>.
</p>

{% if first %}
<p>
We need a few pieces of information from you in order to process a payment:
</p>

<p>
<ul>
<li>The name of the person or organization that will be receiving the payment</li>
<li>The address, including country, for the person or organization</li>
<li>Fill out the payment information in the <a href="{{ settings_url }}">publisher settings</a></li>
</ul>
</p>

<p>
<strong>Please reply to this email with the name & address of the person or organization receiving this payment.</strong>
Once we have this information, we will process the payment.
These will show up in the <a href="{{ payouts_url }}">payouts dashboard</a>,
once they have been started.
</p>

{% else %}

<p>
Since we have already processed a payout for you,
we should have all the information needed start the payout.
You can always update your payout settings in the <a href="{{ settings_url }}">publisher settings</a>.
Payouts will show up in the <a href="{{ payouts_url }}">payouts dashboard</a> for your records once processed.
</p>

{% endif %}

<p>
Thanks again for being part of the EthicalAds network.
</p>

<p>
Cheers,<br>
Eric
</p>
{% endautoescape %}
"""


class Command(BaseCommand):

    """Add a publisher from the command line."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-e", "--email", help="Generate email", required=False, action="store_true"
        )
        parser.add_argument(
            "-s", "--send", help="Send email", required=False, action="store_true"
        )
        parser.add_argument(
            "-p", "--payout", help="Create payouts", required=False, action="store_true"
        )
        parser.add_argument(
            "--publisher", help="Specify a specific publisher", required=False
        )
        parser.add_argument(
            "-a",
            "--all",
            help="Output payouts for all publishers",
            required=False,
            action="store_true",
        )
        parser.add_argument(
            "-d",
            "--debug",
            help="Print debug output",
            required=False,
            action="store_true",
        )

    def handle(self, *args, **kwargs):
        # pylint: disable=too-many-statements,too-many-branches
        print_email = kwargs.get("email")
        send_email = kwargs.get("send")
        create_payout = kwargs.get("payout")
        all_publishers = kwargs.get("all")
        publisher_slug = kwargs.get("publisher")
        debug = kwargs.get("debug")

        self.stdout.write("Processing payouts. \n")

        queryset = Publisher.objects.all()
        if publisher_slug:
            queryset = queryset.filter(slug__contains=publisher_slug)

        for publisher in queryset:
            data = generate_publisher_payout_data(publisher)
            report = data.get("due_report")
            report_url = data.get("due_report_url")
            if not report:
                if not all_publishers:
                    if debug:
                        self.stdout.write(
                            f"Skipping for no due report: {publisher.slug}\n"
                        )
                    # Skip publishers without due money
                    continue
                report = data.get("current_report")
                report_url = data.get("current_report_url")

            due_balance = report["total"]["revenue_share"]
            due_str = "{:.2f}".format(due_balance)
            ctr = report["total"]["ctr"]
            first = data.get("first")

            if due_balance < float(50) and not all_publishers:
                if debug:
                    self.stdout.write(
                        f"Skipping for low balance: {publisher.slug} owed {due_str}\n"
                    )
                continue

            self.stdout.write("\n\n###########\n")
            self.stdout.write(str(publisher) + "\n")
            self.stdout.write(
                "total={:.2f}".format(due_balance)
                + " ctr={:.3f}".format(ctr)
                + " first={}".format(first)
                + "\n"
            )
            self.stdout.write(report_url + "\n")
            self.stdout.write("###########\n\n")

            if print_email or send_email:
                payouts_url = generate_absolute_url(
                    "publisher_payouts", kwargs={"publisher_slug": publisher.slug}
                )
                settings_url = generate_absolute_url(
                    "publisher_settings", kwargs={"publisher_slug": publisher.slug}
                )
                context = dict(
                    report=report,
                    report_url=report_url,
                    payouts_url=payouts_url,
                    settings_url=settings_url,
                    publisher=publisher,
                    **data,
                )
                if ctr < 0.08:
                    self.stdout.write("Include CTR callout?\n")
                    ctr_proceed = input("y/n?: ")
                    if ctr_proceed == "y":
                        context["ctr"] = ctr

                email_html = (
                    Template(email_template)
                    .render(Context(context))
                    .replace("\n\n", "\n")
                )

            if print_email:
                self.stdout.write(email_html)

            if send_email:
                token = getattr(settings, "FRONT_TOKEN")
                channel = getattr(settings, "FRONT_CHANNEL")
                author = getattr(settings, "FRONT_AUTHOR")

                if not token or not channel:
                    self.stdout.write("No front token, not sending email\n")
                    return

                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }

                payload = {
                    # "to": ['eric@ericholscher.com'], # For testing
                    "to": [user.email for user in publisher.user_set.all()],
                    "sender_name": "EthicalAds by Read the Docs",
                    "subject": f"EthicalAds Payout - {publisher.name}",
                    "options": {"archive": True},
                    "body": email_html,
                }
                if author:
                    payload["author_id"] = author

                url = f"https://api2.frontapp.com/channels/{channel}/messages"

                self.stdout.write("Send email?\n")
                self.stdout.write(f"{payload['to']}: {payload['subject']}\n")
                proceed = input("y/n?: ")
                if not proceed == "y":
                    self.stdout.write("Skipping email.\n")
                else:
                    requests.request("POST", url, json=payload, headers=headers)
                    # pprint(response.json())

            # Don't show payouts on first-time users unless we're specifically targeting them
            if create_payout and (publisher_slug or not first):
                self.stdout.write("Create Payout?\n")

                if publisher.payout_method:
                    if publisher.stripe_connected_account_id:
                        self.stdout.write(
                            f"Stripe: https://dashboard.stripe.com/connect/accounts/{publisher.stripe_connected_account_id}\n"
                        )
                    elif publisher.open_collective_name:
                        self.stdout.write(
                            f"Open Collective: https://opencollective.com/{publisher.open_collective_name}\n"
                        )
                    elif publisher.paypal_email:
                        self.stdout.write(f"Paypal: {publisher.paypal_email}\n")
                    else:
                        self.stdout.write(
                            f"Payment method: {publisher.payout_method}\n"
                        )
                    self.stdout.write(due_str)
                    self.stdout.write(f"EthicalAds Payout - {publisher.name}\n")

                payout_proceed = input("y/n?: ")
                if not payout_proceed == "y":
                    self.stdout.write("Skipping payout\n")
                else:
                    publisher.payouts.create(
                        date=timezone.now(),
                        method=publisher.payout_method,
                        amount=due_balance,
                        note=report_url,
                    )
