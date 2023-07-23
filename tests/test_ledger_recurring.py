from click.testing import CliRunner

from ledger_recurring import main


def test_monthly_transactions():
    config_filename = "config.yaml"
    config = """
- name: mortgage
  rule:
    frequency: monthly
    start_date: 2023-01-03
  postings:
    - account: assets:current
      amount: £1000
    - account: liabilities:mortgage
      amount: £-1000
- name: water bill
  rule:
    frequency: monthly
    start_date: 2023-01-10
  postings:
    - account: assets:current
      amount: £-50
    - account: expenses:bills
      amount: £50
"""
    output_filename = "output.ledger"
    month = "2023-02"

    want = "\n".join(
        [
            "2023-02-03 mortgage",
            "\tassets:current\t£1000",
            "\tliabilities:mortgage\t£-1000",
            "",
            "2023-02-10 water bill",
            "\tassets:current\t£-50",
            "\texpenses:bills\t£50",
            "",
        ]
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, output_filename, month])
        assert result.exit_code == 0

        with open(output_filename) as output_file:
            got = output_file.read()

        assert got == want


def test_amount_is_optional():
    config_filename = "config.yaml"
    config = """
- name: mortgage
  rule:
    frequency: monthly
    start_date: 2023-01-03
  postings:
    - account: assets:current
      amount: £1000
    - account: liabilities:mortgage
"""
    output_filename = "output.ledger"
    month = "2023-02"

    want = "\n".join(
        [
            "2023-02-03 mortgage",
            "\tassets:current\t£1000",
            "\tliabilities:mortgage",
            "",
        ]
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, output_filename, month])
        assert result.exit_code == 0

        with open(output_filename) as output_file:
            got = output_file.read()

        assert got == want
