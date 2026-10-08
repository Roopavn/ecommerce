from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_modernize_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_order_id",
            field=models.CharField(max_length=100, null=True, blank=True, unique=True),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_id",
            field=models.CharField(max_length=100, null=True, blank=True, unique=True),
        ),
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
        migrations.AddField(
            model_name="order",
            name="payment_notification_status",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]
}
