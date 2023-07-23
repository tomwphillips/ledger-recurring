# ledger-recurring

A utility I use to generate recurring entries in my [Ledger](https://ledger-cli.org/) files.

Install it from Github:

```
pip install git+https://github.com/tomwphillips/ledger-recurring
```

Specify your recurring transactions in a file like `recurring.yaml`:

```
- name: Council tax
  rule:
    frequency: monthly
    start_date: 2023-01-01
    count: 9
  postings:
    - account: assets:bills
      amount: £-200
    - account: expenses:bills

- name: Yorkshire Water
  rule:
    frequency: monthly
    start_date: 2023-01-09
  postings:
    - account: assets:bills
      amount: £-45
    - account: expenses:bills
```

Then generate the Ledger file for a given month:

```
$ ledger-recurring recurring.yaml postings.ledger 2023-03
$ cat postings.ledger
(venv) tomphillips@Toms-MBP ledger-recurring % cat postings.ledger
2023-03-01 Council tax
    assets:bills    £-200
    expenses:bills

2023-03-09 Yorkshire Water
    assets:bills    £-45
    expenses:bills
```


