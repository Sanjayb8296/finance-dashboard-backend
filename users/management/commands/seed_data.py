import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from records.models import Category, FinancialRecord, RecordType
from users.models import Role, User


class Command(BaseCommand):
    help = "Seed the database with sample users and financial records"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Create users (one per role)
        users_data = [
            {"email": "admin@example.com", "name": "Admin User", "role": Role.ADMIN, "password": "admin123!", "is_staff": True},
            {"email": "manager@example.com", "name": "Manager User", "role": Role.MANAGER, "password": "manager123!"},
            {"email": "analyst@example.com", "name": "Analyst User", "role": Role.ANALYST, "password": "analyst123!"},
            {"email": "viewer@example.com", "name": "Viewer User", "role": Role.VIEWER, "password": "viewer123!"},
            {"email": "auditor@example.com", "name": "Auditor User", "role": Role.AUDITOR, "password": "auditor123!"},
        ]

        created_users = []
        for user_data in users_data:
            password = user_data.pop("password")
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=user_data,
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  Created user: {user.email} ({user.role})"))
            else:
                self.stdout.write(f"  User already exists: {user.email}")
            created_users.append(user)

        # Create financial records for manager and admin
        record_users = [u for u in created_users if u.role in (Role.MANAGER, Role.ADMIN)]

        income_categories = [Category.SALARY, Category.FREELANCE, Category.INVESTMENTS]
        expense_categories = [
            Category.RENT, Category.UTILITIES, Category.GROCERIES,
            Category.TRANSPORT, Category.ENTERTAINMENT, Category.HEALTHCARE,
            Category.EDUCATION, Category.SHOPPING, Category.TRAVEL,
            Category.INSURANCE, Category.TAXES,
        ]

        descriptions = {
            Category.SALARY: ["Monthly salary", "Salary payment", "Base salary"],
            Category.FREELANCE: ["Web development project", "Consulting fee", "Design work"],
            Category.INVESTMENTS: ["Stock dividends", "Interest income", "Investment return"],
            Category.RENT: ["Monthly rent", "Office rent"],
            Category.UTILITIES: ["Electricity bill", "Water bill", "Internet bill"],
            Category.GROCERIES: ["Weekly groceries", "Supermarket shopping"],
            Category.TRANSPORT: ["Gas", "Bus pass", "Uber rides"],
            Category.ENTERTAINMENT: ["Netflix subscription", "Movie tickets", "Concert tickets"],
            Category.HEALTHCARE: ["Doctor visit", "Pharmacy", "Insurance copay"],
            Category.EDUCATION: ["Online course", "Books", "Workshop fee"],
            Category.SHOPPING: ["Clothing", "Electronics", "Home goods"],
            Category.TRAVEL: ["Flight tickets", "Hotel booking", "Travel expenses"],
            Category.INSURANCE: ["Health insurance", "Car insurance"],
            Category.TAXES: ["Income tax", "Property tax"],
        }

        if FinancialRecord.objects.exists():
            self.stdout.write("  Financial records already exist, skipping...")
        else:
            records = []
            today = date.today()
            for user in record_users:
                for month_offset in range(12):
                    record_date = today - timedelta(days=30 * month_offset)

                    # Add income records
                    for cat in income_categories:
                        amount = Decimal(str(random.randint(1000, 10000))) + Decimal("0.00")
                        records.append(
                            FinancialRecord(
                                user=user,
                                amount=amount,
                                type=RecordType.INCOME,
                                category=cat,
                                date=record_date,
                                description=random.choice(descriptions[cat]),
                                tags="monthly,verified" if cat == Category.SALARY else "project",
                            )
                        )

                    # Add expense records
                    for cat in random.sample(expense_categories, k=random.randint(3, 6)):
                        amount = Decimal(str(random.randint(50, 3000))) + Decimal("0.00")
                        records.append(
                            FinancialRecord(
                                user=user,
                                amount=amount,
                                type=RecordType.EXPENSE,
                                category=cat,
                                date=record_date - timedelta(days=random.randint(0, 15)),
                                description=random.choice(descriptions[cat]),
                                tags="recurring" if cat in (Category.RENT, Category.UTILITIES) else "",
                            )
                        )

            FinancialRecord.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(f"  Created {len(records)} financial records"))

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
