"""Seed database with test data."""

from src.database.connection import DatabaseConnection
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.item_repo import ItemRepository
from src.database.repositories.rule_repo import ConsumptionRuleRepository
from src.database.repositories.user_repo import UserRepository


def seed_database(db: DatabaseConnection) -> None:
    """Seed database with test data."""
    session = db.get_session()
    try:
        user_repo = UserRepository(db)
        rule_repo = ConsumptionRuleRepository(db)
        category_repo = CategoryRepository(db)
        item_repo = ItemRepository(db)

        owner = user_repo.create(session, name="Owner", priority=1)
        wife = user_repo.create(session, name="Wife", priority=2)

        rules = [
            rule_repo.create(session, "Скоропорт (5%/день)", "percentage_daily", 5.0),
            rule_repo.create(session, "Среднее (2%/день)", "percentage_daily", 2.0),
            rule_repo.create(session, "Долгое (0.5%/день)", "percentage_daily", 0.5),
            rule_repo.create(session, "Не портится (0%)", "percentage_daily", 0.0),
            rule_repo.create(session, "Ручное", "manual", 0.0),
        ]

        categories = [
            category_repo.create(session, "Молочные продукты", default_consumption_rule_id=rules[0].id),
            category_repo.create(session, "Детское питание", default_consumption_rule_id=rules[2].id),
            category_repo.create(session, "Мясо/Птица/Рыба", default_consumption_rule_id=rules[1].id),
            category_repo.create(session, "Крупы/Макароны/Хлеб", default_consumption_rule_id=rules[2].id),
            category_repo.create(session, "Овощи/Фрукты", default_consumption_rule_id=rules[0].id),
            category_repo.create(session, "Бакалея", default_consumption_rule_id=rules[2].id),
            category_repo.create(session, "Бытовая химия", default_consumption_rule_id=rules[3].id),
            category_repo.create(session, "Гигиена", default_consumption_rule_id=rules[3].id),
            category_repo.create(session, "Напитки", default_consumption_rule_id=rules[2].id),
            category_repo.create(session, "Снеки/Сладости", default_consumption_rule_id=rules[2].id),
        ]

        items = [
            {"name": "Молоко", "category": 0, "package_size": 1.0, "unit": "л", "rule": 0, "stock": 1.0},
            {"name": "Кефир", "category": 0, "package_size": 0.5, "unit": "л", "rule": 0, "stock": 1.0},
            {"name": "Йогурт", "category": 0, "package_size": 1.0, "unit": "шт", "rule": 0, "stock": 6.0},
            {"name": "Творог", "category": 0, "package_size": 0.2, "unit": "кг", "rule": 0, "stock": 0.4},
            {"name": "Пюре детское", "category": 1, "package_size": 1.0, "unit": "шт", "rule": 2, "stock": 10.0},
            {"name": "Каша детская", "category": 1, "package_size": 0.4, "unit": "кг", "rule": 2, "stock": 0.8},
            {"name": "Подгузники", "category": 7, "package_size": 1.0, "unit": "упак", "rule": 3, "stock": 2.0},
            {"name": "Влажные салфетки", "category": 7, "package_size": 1.0, "unit": "упак", "rule": 3, "stock": 3.0},
            {"name": "Стиральный порошок", "category": 6, "package_size": 1.5, "unit": "кг", "rule": 3, "stock": 3.0},
            {"name": "Туалетная бумага", "category": 6, "package_size": 1.0, "unit": "упак", "rule": 3, "stock": 4.0},
        ]

        for item_data in items:
            item_repo.create(
                session,
                name=item_data["name"],
                category_id=categories[item_data["category"]].id,
                package_size=item_data["package_size"],
                unit=item_data["unit"],
                consumption_rule_id=rules[item_data["rule"]].id,
                created_by=owner.id,
            )
            if item_data["stock"] > 0:
                item = item_repo.get_by_name(session, item_data["name"])
                if item:
                    item.current_stock = item_data["stock"]

        session.commit()
        print(f"Created {len(categories)} categories, {len(items)} items, {len(rules)} rules, 2 users")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
