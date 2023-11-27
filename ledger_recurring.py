from datetime import timedelta

import click
import yaml
from dateutil import rrule
from marshmallow import Schema, fields, post_load


class Posting:
    def __init__(self, account, amount=None):
        self.account = account
        self.amount = amount

    def to_ledger_entry(self):
        if self.amount:
            return f"\t{self.account}\t{self.amount}"
        return f"\t{self.account}"


class RecurringTransaction:
    def __init__(self, name, rule, postings, comment=None):
        self.name = name
        self.rule = rule
        self.postings = postings
        self.comment = comment

    def to_ledger_comment(self):
        return (
            [f"\t; {line}" for line in self.comment.splitlines()]
            if self.comment
            else []
        )


class RuleSchema(Schema):
    frequency = fields.String(required=True)
    start_date = fields.Raw(required=True)  # pyyaml converts to datetime.date
    count = fields.Integer()
    by_month_day = fields.Integer()

    @post_load
    def make_rrule(self, data, **kwargs):
        return rrule.rrule(
            freq=getattr(rrule, data["frequency"].upper()),
            dtstart=data["start_date"],
            count=data.get("count"),
            bymonthday=data.get("by_month_day"),
        )


class PostingSchema(Schema):
    account = fields.String(required=True)
    amount = fields.String()

    @post_load
    def make_posting(self, data, **kwargs):
        return Posting(**data)


class RecurringTransactionSchema(Schema):
    name = fields.String(required=True)
    rule = fields.Nested(RuleSchema, required=True)
    postings = fields.List(fields.Nested(PostingSchema), required=True)
    comment = fields.String()

    @post_load
    def make_recurring_transaction(self, data, **kwargs):
        return RecurringTransaction(**data)


@click.command()
@click.argument("config_file", type=click.File("r"))
@click.argument("month", type=click.DateTime(formats=["%Y-%m"]))
@click.argument("output_file", type=click.File("w"), default="-")
@click.option(
    "-s",
    "--state",
    "transaction_state",
    type=click.Choice(["!", "*", None]),
    default=None,
)
def main(config_file, month, output_file, transaction_state=None):
    config_schema = RecurringTransactionSchema(many=True)
    config = config_schema.load(yaml.safe_load(config_file))

    after = month.replace(day=1)

    if after.month == 12:
        before = after.replace(year=after.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        before = after.replace(month=after.month + 1) - timedelta(days=1)

    ledger = []
    for recurring_transaction in config:
        postings = [
            posting.to_ledger_entry() for posting in recurring_transaction.postings
        ]
        dates = recurring_transaction.rule.between(after, before, inc=True)
        for date in dates:
            top_line = (
                f"{date.date()}"
                + (f" {transaction_state}" if transaction_state else "")
                + f" {recurring_transaction.name}"
            )
            ledger.append(top_line)
            ledger.extend(recurring_transaction.to_ledger_comment())
            ledger.extend(postings)
            ledger.append("")

    output_file.write("\n".join(ledger))


if __name__ == "__main__":
    main()
