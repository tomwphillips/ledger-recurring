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

        result = runner.invoke(main, [config_filename, month])
        assert result.exit_code == 0
        assert result.output == want


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

        result = runner.invoke(main, [config_filename, month])
        assert result.exit_code == 0
        assert result.output == want


def test_count_occurrences():
    config_filename = "config.yaml"
    config = """
- name: mortgage
  rule:
    frequency: monthly
    start_date: 2023-01-03
    count: 3
  postings:
    - account: assets:current
      amount: £1000
    - account: liabilities:mortgage
"""
    month_last_occurence = "2023-03"
    want_last_occurence = "\n".join(
        [
            "2023-03-03 mortgage",
            "\tassets:current\t£1000",
            "\tliabilities:mortgage",
            "",
        ]
    )

    runner = CliRunner()

    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, month_last_occurence])
        assert result.exit_code == 0
        assert result.output == want_last_occurence

    month_after_last_occurence = "2023-04"
    want_after_last_occurence = ""

    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, month_after_last_occurence])
        assert result.exit_code == 0
        assert result.output == want_after_last_occurence


def test_last_day_of_the_month():
    config_filename = "config.yaml"
    config = """
- name: savings
  rule:
    frequency: monthly
    start_date: 2023-01-28
    by_month_day: -1
  postings:
    - account: assets:current
      amount: £100
    - account: assets:savings
"""
    tests = [
        ("2023-02", "2023-02-28 savings\n\tassets:current\t£100\n\tassets:savings\n"),
        ("2023-03", "2023-03-31 savings\n\tassets:current\t£100\n\tassets:savings\n"),
        ("2023-04", "2023-04-30 savings\n\tassets:current\t£100\n\tassets:savings\n"),
    ]

    runner = CliRunner()

    for month, want in tests:
        with runner.isolated_filesystem():
            with open(config_filename, "w") as config_file:
                config_file.write(config)

            result = runner.invoke(main, [config_filename, month])
            assert result.exit_code == 0
            assert result.output == want


def test_comments():
    config_filename = "config.yaml"
    config = """
- name: mortgage
  comment: |
    line 1 comment
    line 2 comment
    line 3 comment
  rule:
    frequency: monthly
    start_date: 2023-01-03
  postings:
    - account: assets:current
      amount: £1000
    - account: liabilities:mortgage
      amount: £-1000
"""
    month = "2023-02"

    want = "\n".join(
        [
            "2023-02-03 mortgage",
            "\t; line 1 comment",
            "\t; line 2 comment",
            "\t; line 3 comment",
            "\tassets:current\t£1000",
            "\tliabilities:mortgage\t£-1000",
            "",
        ]
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, month])
        assert result.exit_code == 0
        assert result.output == want


def test_output_to_file_instead_of_stdout():
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

        result = runner.invoke(main, [config_filename, month, output_filename])
        assert result.exit_code == 0

        with open(output_filename) as output_file:
            got = output_file.read()

        assert got == want


def test_pending_transaction_state():
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
"""
    month = "2023-02"
    want = "\n".join(
        [
            "2023-02-03 ! mortgage",
            "\tassets:current\t£1000",
            "\tliabilities:mortgage\t£-1000",
            "",
        ]
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, month, "-s", "!"])
        assert result.exit_code == 0
        assert result.output == want


def test_monthly_transactions_in_december():
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
"""
    month = "2023-12"

    want = "\n".join(
        [
            "2023-12-03 mortgage",
            "\tassets:current\t£1000",
            "\tliabilities:mortgage\t£-1000",
            "",
        ]
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(config_filename, "w") as config_file:
            config_file.write(config)

        result = runner.invoke(main, [config_filename, month])
        assert result.exit_code == 0
        assert result.output == want
