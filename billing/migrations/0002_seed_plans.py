from django.db import migrations


def seed_plans(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')

    def upsert(name, tier, user_type, price, interval, description):
        obj, _ = Plan.objects.get_or_create(tier=tier, user_type=user_type, defaults={
            'name': name,
            'price': price,
            'interval': interval,
            'description': description,
        })
        if _ is False:
            obj.name = name
            obj.price = price
            obj.interval = interval
            obj.description = description
            obj.save()

    upsert('Farmer Free', 1, 'farmer', 0, 'monthly', 'Basic access, limited recommendations')
    upsert('Farmer Standard', 2, 'farmer', 150000, 'monthly', 'Expanded features and advisory')
    upsert('Farmer Premium', 3, 'farmer', 500000, 'monthly', 'Full features and priority support')

    upsert('Buyer Free', 1, 'buyer', 0, 'monthly', 'Basic access for listings')
    upsert('Buyer Standard', 2, 'buyer', 200000, 'monthly', 'Enhanced tools and analytics')
    upsert('Buyer Premium', 3, 'buyer', 700000, 'monthly', 'Advanced analytics and support')

    upsert('Org Free', 1, 'org', 0, 'monthly', 'Limited API access')
    upsert('Org Pro', 2, 'org', 5000000, 'monthly', 'Paid API access with higher limits')


def unseed_plans(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')
    Plan.objects.filter(user_type__in=['farmer', 'buyer', 'org']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_plans, reverse_code=unseed_plans),
    ]

