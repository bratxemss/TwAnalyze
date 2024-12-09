import argparse
import asyncio
from .models import Customer,Tweet
from .visual import TwitterApp

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-run", required=False, action="store_true")
    parser.add_argument("-init_db", required=False, action="store_true")

    return parser


async def create_db():
    await Customer.create_table()
    await Tweet.create_table()


if __name__ == "__main__":
    parser = args_parser()
    namespace = parser.parse_args()

    if namespace.run:
        app = TwitterApp()
        app.mainloop()

    if namespace.init_db:
        asyncio.run(create_db())