from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0005_payment_amount_currency"),
    ]

    operations = [
        migrations.CreateModel(
            name="RazorpayWebhookEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_id", models.CharField(max_length=100, unique=True)),
                ("event", models.CharField(max_length=100)),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
