from backend.app.database.connection import SessionLocal
from backend.app.models.user import User
from backend.app.service.auth_service import hash_password


# ============================================================
# DEFAULT DEVELOPMENT USERS
# ============================================================

USERS = [
    {
        "username": "admin",
        "email": "admin@evchain.example.com",
        "password": "Admin@123",
        "full_name": "System Administrator",
        "role": "ADMIN"
    },
    {
        "username": "procurement",
        "email": "procurement@evchain.example.com",
        "password": "Procurement@123",
        "full_name": "Procurement Manager",
        "role": "PROCUREMENT_MANAGER"
    },
    {
        "username": "inventory",
        "email": "inventory@evchain.example.com",
        "password": "Inventory@123",
        "full_name": "Inventory Manager",
        "role": "INVENTORY_MANAGER"
    },
    {
        "username": "analyst",
        "email": "analyst@evchain.example.com",
        "password": "Analyst@123",
        "full_name": "Supply Chain Analyst",
        "role": "ANALYST"
    }
]


# ============================================================
# SEED USERS
# ============================================================

def main():

    db = SessionLocal()

    try:

        print("\n============================================")
        print("EV SUPPLY CHAIN - USER SEED")
        print("============================================\n")

        for item in USERS:

            # Check whether user already exists
            existing_user = (
                db.query(User)
                .filter(User.email == item["email"])
                .first()
            )

            if existing_user:

                print(
                    f"Already exists: "
                    f"{item['email']} "
                    f"[{existing_user.role}]"
                )

                continue

            # Create new user
            user = User(
                username=item["username"],
                email=item["email"],
                password_hash=hash_password(
                    item["password"]
                ),
                full_name=item["full_name"],
                role=item["role"],
                is_active=True
            )

            db.add(user)

            print(
                f"Created: "
                f"{item['email']} "
                f"[{item['role']}]"
            )

        # Save all users
        db.commit()

        print("\n============================================")
        print("USER SEED COMPLETE")
        print("============================================")

    except Exception as exc:

        db.rollback()

        print("\n============================================")
        print("USER SEED FAILED")
        print("============================================")

        print(f"Error: {exc}")

        raise

    finally:

        db.close()


# ============================================================
# RUN SCRIPT
# ============================================================

if __name__ == "__main__":
    main()