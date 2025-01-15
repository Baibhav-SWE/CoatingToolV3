document.addEventListener('DOMContentLoaded', () => {
  function configureSubscriptionDrawer(event) {
    const drawer = document.getElementById('subscription-drawer-navigation');
    const title = document.getElementById('subscription-drawer-title');
    const overlay = document.getElementById('drawer-overlay');
    const closeDrawerBtn = document.getElementById('close-drawer-btn');
    const monthlyRateDivs = document.querySelectorAll('.monthly-rate');
    const yearlyRateDiv = document.getElementById('yearly-rate');
    const yearlyAffectedMonthlyRate = document.getElementById('yearly-affected-monthly-rate');
    const subscriptionTypeInput = document.getElementById('subscription-type');
    const type = event.target.dataset.type;

    const plans = {
      "basic": {
        "title": "Basic",
        "prices": {
          "monthly": 20.00,
          "yearly": 200.00
        },
        "checkoutLinks": {
          "monthly": "https://intelladapt.myshopify.com/cart/43091539918947:1?channel=buy_button",
          "yearly": "https://intelladapt.myshopify.com/cart/43091539918947:1?channel=buy_button"
        }
      },
      "premium": {
        "title": "Premium",
        "prices": {
          "monthly": 30.00,
          "yearly": 300.00
        },
        "checkoutLinks": {
          "monthly": "https://intelladapt.myshopify.com/cart/43091539918947:1?channel=buy_button",
          "yearly": "https://intelladapt.myshopify.com/cart/43091539918947:1?channel=buy_button"
        }
      }
    }
    const plan = plans[type];
    monthlyRateDivs.forEach(div => div.innerText = `$${plan.prices.monthly.toFixed(2)}`);
    yearlyRateDiv.innerText = `$${plan.prices.yearly.toFixed(2)}`;
    yearlyAffectedMonthlyRate.innerText = `$${(plan.prices.yearly / 12).toFixed(2)}`;
    subscriptionTypeInput.value = type;
    title.innerText = `${plan.title} Plan`;
    drawer.classList.remove('translate-x-full');
    overlay.classList.remove('hidden');

    const closeDrawer = () => {
      drawer.classList.add('translate-x-full');
      overlay.classList.add('hidden');
    };

    // Open drawer

    // Close drawer when clicking the close button
    closeDrawerBtn.addEventListener('click', closeDrawer);

    // Close drawer when clicking outside of it (overlay)
    overlay.addEventListener('click', closeDrawer);
  }

  const showDrawerBtns = document.querySelectorAll('.show-subscription-drawer-btn');
  showDrawerBtns.forEach((button) => button.addEventListener('click', configureSubscriptionDrawer));

  const totalCost = document.getElementById('total-cost');
  document.querySelectorAll('input[name="plan"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      // Remove highlight from all cards
      document.querySelectorAll('.price-card').forEach(card => {
        card.classList.remove("bg-gray-600");
      });

      // Add highlight to selected card
      e.target.closest('.price-card').classList.add("bg-gray-600");
    });
  });
  // Trigger change event on the checked radio button to highlight initial selection
  document.querySelector('input[name="plan"]:checked').dispatchEvent(new Event('change'));
  document.getElementById("subscription-form").addEventListener("submit", function (event) {
    const submitButton = document.getElementById("subscription-drawer-submit");
    const loader = document.getElementById("subscription-drawer-submit-loader");

    submitButton.disabled = true; // Disable the button
    loader.classList.remove("hidden"); // Show the loader
  });
  window.addEventListener("pageshow", function () {
    const submitButton = document.getElementById("subscription-drawer-submit");
    const loader = document.getElementById("subscription-drawer-submit-loader");

    submitButton.disabled = false; // Enable the button
    loader.classList.add("hidden"); // Hide the loader
  });
});