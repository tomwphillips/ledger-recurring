from datetime import date, datetime, time, timedelta
import click
import yaml
from dateutil import rrule
from marshmallow import Schema, fields, post_load


class Posting:
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

    def to_ledger_entry(self):
        return f"\t{self.account}\t{self.amount}"


class RecurringTransaction:
    def __init__(self, name, rule, postings):
        self.name = name
        self.rule = rule
        self.postings = postings


class RuleSchema(Schema):
    frequency = fields.String(required=True)
    start_date = fields.Raw(required=True)  # pyyaml converts to datetime.date

    @post_load
    def make_rrule(self, data, **kwargs):
        return rrule.rrule(
            freq=getattr(rrule, data["frequency"].upper()),
            dtstart=data["start_date"],
        )


class PostingSchema(Schema):
    account = fields.String(required=True)
    amount = fields.Decimal(required=True)

    @post_load
    def make_posting(self, data, **kwargs):
        return Posting(**data)


class RecurringTransactionSchema(Schema):
    name = fields.String(required=True)
    rule = fields.Nested(RuleSchema, required=True)
    postings = fields.List(fields.Nested(PostingSchema), required=True)

    @post_load
    def make_recurring_transaction(self, data, **kwargs):
        return RecurringTransaction(**data)


@click.command()
@click.argument("config_file", type=click.File("r"))
@click.argument("output_file", type=click.File("w"))
@click.argument("month", type=click.DateTime(formats=["%Y-%m"]))
def main(config_file, output_file, month):
    config_schema = RecurringTransactionSchema(many=True)
    config = config_schema.load(yaml.safe_load(config_file))

    after = month.replace(day=1)
    before = after.replace(month=after.month + 1) - timedelta(days=1)

    ledger = []
    for recurring_transaction in config:
        postings = [
            posting.to_ledger_entry() for posting in recurring_transaction.postings
        ]
        dates = recurring_transaction.rule.between(after, before, inc=True)
        for date in dates:
            ledger.append(f"{date.date()} {recurring_transaction.name}")
            ledger.extend(postings)
            ledger.append("")

    output_file.write("\n".join(ledger))


if __name__ == "__main__":
    main()
