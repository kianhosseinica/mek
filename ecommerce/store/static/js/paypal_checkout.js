document.addEventListener("DOMContentLoaded", function () {
    const paypalButtonContainer = document.getElementById("paypal-button-container");
    const placeOrderBtn = document.getElementById("place-order-btn");
    const paypalOption = document.getElementById("paypal-option");
    const checkoutForm = document.getElementById("checkout-form");

    // Show PayPal button when PayPal is selected
    document.querySelectorAll("input[name='payment_method']").forEach((input) => {
        input.addEventListener("change", function () {
            if (paypalOption.checked) {
                paypalButtonContainer.style.display = "block";
                placeOrderBtn.style.display = "none"; // Hide normal order button
            } else {
                paypalButtonContainer.style.display = "none";
                placeOrderBtn.style.display = "block"; // Show normal order button
            }
        });
    });

    // Render PayPal Button
    paypal.Buttons({
        style: {
            layout: 'vertical', // Stack buttons vertically
            color:  'gold',
            shape:  'rect',
            label:  'pay',
        },
        createOrder: function (data, actions) {
            return fetch("/create-paypal-order/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    total: document.querySelector("[data-title='Total'] span").textContent.trim().replace("$", "")
                })
            })
            .then(response => response.json())
            .then(order => order.id);
        },

        onApprove: function (data, actions) {
            return fetch("/capture-paypal-order/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    orderID: data.orderID
                })
            })
            .then(response => response.json())
            .then(details => {
                document.getElementById("result-message").innerHTML = "Transaction completed by " + details.payer.name.given_name;

                // Auto-submit the form after successful PayPal payment
                checkoutForm.submit();
            });
        }
    }).render("#paypal-button-container");

    function getCSRFToken() {
        return document.querySelector("input[name='csrfmiddlewaretoken']").value;
    }
});
