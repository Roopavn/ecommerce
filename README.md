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


## Production checklist

Before enabling live payments:

1. Run `python manage.py migrate`.
2. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS`.
3. Configure `DATABASE_URL` for PostgreSQL (SQLite remains available for local development).
4. Configure Razorpay live credentials and the verified webhook endpoint.
5. Configure SMTP credentials for payment notifications.
6. Run `python manage.py check --deploy` and the test suite.
7. Verify successful, failed, cancelled, duplicate-webhook, and amount-mismatch payment scenarios in Razorpay Test Mode before switching to live mode.
8. Never commit Razorpay, SMTP, AWS, or Django secrets to Git.
