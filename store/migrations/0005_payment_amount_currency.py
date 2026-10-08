from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_payment_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_currency",
            field=models.CharField(default="INR", max_length=3),
        ),
    ]
