"""View class names and descriptions for every table in the database."""

from inspect import getdoc
from t import get_classes


def main():
    print('Database classes:')
    for cls in get_classes():
        print(f'{cls.__name__} ({cls.__table__.name})')
        print(getdoc(cls))
        print()


if __name__ == '__main__':
    main()
