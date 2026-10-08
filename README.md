# ecommerce web application: 
It is web based application. The primary goal of ecommerce is to sell goods online. 
This product deals with developing e-commerce website for online product sell.
It is provides the user with catalog of different product available for purchase in the store. 
And it is a way to keep our items on your shopping cart.
It perform add and remove products also functionality to increase or decrease the number of items.
In order of facility on online purchase a shopping cart is provides to user.


## Payment and email notifications

Razorpay payments support UPI, cards, net banking and other enabled Razorpay payment methods.

Required environment variables:

- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `RAZORPAY_WEBHOOK_SECRET`
- `EMAIL_HOST`
- `EMAIL_PORT` (default: 587)
- `EMAIL_USE_TLS` (default: True)
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

Payment notifications are sent from the Django backend after a verified payment success or a verified Razorpay payment failure webhook. SMTP credentials must be stored as deployment secrets/environment variables and never committed to the repository.
