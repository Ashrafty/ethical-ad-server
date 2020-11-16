"""
List all payouts.

Example::

    # List all active payouts
    ./manage.py payouts

    # List all active payouts and show the email
    ./manage.py payouts --email
"""
from django.core.management.base import BaseCommand
from django.template import Context
from django.template import Template

from ...models import Publisher
from ...utils import generate_publisher_payout_data
from adserver.utils import generate_absolute_url

email_template = """

Thanks for being one of the first publishers on our EthicalAds network. We aim to get payouts completed by the 15th of the month, as noted in our [publisher policy](https://www.ethicalads.io/publisher-policy/). If you haven't had a chance to look it over, please do, as it sets expectations around ad placements and payments.

{% if ctr < .06 %}

As noted in our publisher policy, we expect all our publishers to maintain a CTR (click though rate) around or above .1%. Your CTR is currently {{ report.total.ctr|floatformat:3 }}%, which is below our current minimum. We're working on documenting some recommendations for improving CTR, but for now the primary thing is making sure your ads are displayed in a prominent place, and appropriate for each screen size.

{% endif %}

We are now processing payments for **{{ today|date:"F" }} {{ today|date:"Y" }}**, and you made a total of **${{ report.total.revenue_share|floatformat:2 }}** for ads displayed between {{ last_payout_date|date:"F j" }}-{{ last_day_last_month|date:"F j" }}. You can find the full report for this billing cycle on our [reports page]({{ url }}).

{% if first %}
We need a few pieces of information from you in order to process a payment:
* The name of the person or organization that will be receiving the payment
* The address, including country, for the person/organization
* Fill out the payment information in the [publisher settings]({{ settings_url }})

Once we have this information, we will process the payment. These will show up in the [Payouts dashboard]({{ payouts_url }}), once they have been started.

{% else %}

Since we have already processed a payout for you, we should have all the information needed to move ahead. You can always update your payout settings in the [publisher settings]({{ settings_url }}). Payouts will show up in the [payouts dashboard]({{ payouts_url }}) for your records.

{% endif %}

Thanks again for being part of the EthicalAds network, and we look forward to many more months of payouts!

Cheers,
Eric

"""


class Command(BaseCommand):

    """Add a publisher from the command line."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-e", "--email", help="Generate email", required=False, action="store_true"
        )
        parser.add_argument(
            "-a",
            "--all",
            help="Output payouts for all publishers",
            required=False,
            action="store_true",
        )

    def handle(self, *args, **kwargs):
        email = kwargs.get("email")
        all_publishers = kwargs.get("all")
        self.stdout.write("Processing payouts. \n")
        for publisher in Publisher.objects.all():
            data = generate_publisher_payout_data(publisher)
            report = data.get("due_report")
            url = data.get("due_report_url")
            if not report:
                if not all_publishers:
                    # Skip publishers without due money
                    continue
                report = data.get("current_report")
                url = data.get("current_report_url")

            due_balance = report["total"]["revenue_share"]
            ctr = report["total"]["ctr"]

            if due_balance > float(50):
                self.stdout.write("###########" + "\n")
                self.stdout.write(str(publisher) + "\n")
                self.stdout.write(
                    "total={:.2f}".format(due_balance)
                    + " ctr={:.3f}".format(ctr)
                    + " first={}".format(data.get("first"))
                    + "\n"
                )
                self.stdout.write(url + "\n")
                self.stdout.write("###########" + "\n" + "\n")
                if email:
                    payouts_url = generate_absolute_url(
                        "publisher_payouts", kwargs={"publisher_slug": publisher.slug}
                    )
                    settings_url = generate_absolute_url(
                        "publisher_settings", kwargs={"publisher_slug": publisher.slug}
                    )
                    self.stdout.write(
                        Template(email_template).render(
                            Context(
                                dict(
                                    report=report,
                                    url=url,
                                    payouts_url=payouts_url,
                                    settings_url=settings_url,
                                    ctr=ctr,
                                    **data,
                                )
                            )
                        )
                    )
