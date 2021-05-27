"""Views for the administrator actions."""
import stripe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from ..models import Advertiser
from ..models import Campaign
from ..models import Flight
from ..models import PublisherGroup


User = get_user_model()


class CreateAdvertiserForm(forms.Form):

    """
    Creates an advertiser.

    This isn't a simple model form because it creates a few additional objects as well
    such as a user (needed to create a stripe account), campaign, and initial flight.
    """

    DEFAULT_CPM = 3.33
    DEFAULT_NUM_IMPRESSIONS = 300000
    DEFAULT_COUNTRY_TARGETING = [
        # North America
        "US",
        "CA",
        # Core Europe
        "DE",
        "GB",
        "FR",
        "IT",
        "ES",
        "CH",
        "NL",
        "PT",
        "AT",
        "BE",
        "IE",
        "GR",
        "SE",
        "DK",
        "NO",
        "FI",
        # Bundled into Europe
        "IL",
        # Australia and New Zealand
        "AU",
        "NZ",
    ]

    # Advertiser information
    advertiser_name = forms.CharField(label=_("Advertiser name"), max_length=200)

    # User information
    user_name = forms.CharField(label=_("Name"), max_length=200)
    user_email = forms.EmailField(label=_("Email"))

    def __init__(self, *args, **kwargs):
        """Add the form helper and customize the look of the form."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Fieldset(
                _("Advertiser information"),
                Field("advertiser_name", placeholder=_("Company name")),
                css_class="my-3",
            ),
            Fieldset(
                _("Managing user"),
                Field("user_name"),
                Field("user_email", placeholder="advertiser@company.com"),
                css_class="my-3",
            ),
            Submit("submit", _("Create advertiser")),
            HTML(
                "<p class='form-text small text-muted'>"
                + str(
                    _(
                        "Creates an advertiser, a campaign, user account, and initial flight. "
                        "The user will receive an invitation email."
                    )
                )
                + "</p>"
            ),
        )

    def clean_advertiser_name(self):
        advertiser_name = self.cleaned_data["advertiser_name"].strip()

        if Advertiser.objects.filter(name=advertiser_name).exists():
            raise forms.ValidationError(_("Advertiser already exists"))

        return advertiser_name

    def create_user(self):
        """Create the user account and send an invite email."""
        user_name = self.cleaned_data["user_name"].strip()
        user_email = self.cleaned_data["user_email"]
        user = User.objects.create_user(name=user_name, email=user_email, password="")
        if hasattr(user, "invite_user"):
            user.invite_user()
        return user

    def create_advertiser(self):
        """Create the advertiser, campaign, and initial flight."""
        advertiser_name = self.cleaned_data["advertiser_name"].strip()

        advertiser = Advertiser.objects.create(
            name=advertiser_name, slug=slugify(advertiser_name)
        )
        campaign = Campaign.objects.create(
            advertiser=advertiser,
            name=advertiser_name,
            slug=slugify(advertiser_name),
        )
        for pub_group in PublisherGroup.objects.all():
            campaign.publisher_groups.add(pub_group)

        flight_name = f"{advertiser_name} Initial Flight"
        Flight.objects.create(
            campaign=campaign,
            name=flight_name,
            slug=slugify(flight_name),
            cpm=self.DEFAULT_CPM,
            sold_impressions=self.DEFAULT_NUM_IMPRESSIONS,
            targeting_parameters={
                "include_countries": self.DEFAULT_COUNTRY_TARGETING,
            },
        )

        return advertiser

    def create_stripe_customer(self, user, advertiser):
        """Setup a Stripe customer for this user."""
        if not settings.STRIPE_SECRET_KEY:
            return None

        stripe_customer = stripe.Customer.create(
            name=user.name,
            email=user.email,
            description=f"Advertising @ {advertiser.name}",
        )
        return stripe_customer

    def save(self):
        """Create the advertiser and associated objects. Send the invitation to the user account."""
        advertiser = self.create_advertiser()
        user = self.create_user()

        if settings.STRIPE_SECRET_KEY:
            # Attach Stripe customer record to the advertiser
            stripe_customer = self.create_stripe_customer(user, advertiser)
            advertiser.stripe_customer_id = stripe_customer.id
            advertiser.save()

        user.advertisers.add(advertiser)

        return advertiser
