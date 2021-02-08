# _*_ coding: utf-8 _*_

"""Console script for semanticbits_assessment."""
from semanticbits_assessment.processors import HealthProcessor
from logging.config import fileConfig
import click
import sys

fileConfig('logging.ini')


@click.group()
def main(args=None):
    return 0


@main.command()
@click.option('--data', type=click.Path(resolve_path=True, exists=True, dir_okay=False))
def load_data(data):
    try:
        hp = HealthProcessor(data)
        hp.run()
    except Exception as exc:
        click.secho(str(exc), fg='red', err=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
