# Email Client

A simplified email client that can summarize unread emails and respond to the oldest unread email.

## Features

- Check and display information about unread emails
- Read the most recent email
- Summarize all unread emails using OpenAI's GPT-4.1-mini model
- Respond to the oldest unread email
- Mark emails as read after responding

## Usage

The email client can be run with the following command-line flags:

```bash
# To check unread emails
python email_client.py --check

# To read the most recent email
python email_client.py --recent

# To summarize all unread emails
python email_client.py --summarize

# To respond to the oldest unread email
python email_client.py --respond

# To do multiple operations
python email_client.py --check --summarize --respond
```

### Examples

1. Check unread emails:
```bash
python email_client.py --check
```

2. Read the most recent email:
```bash
python email_client.py --recent
```

3. Summarize all unread emails:
```bash
python email_client.py --summarize
```

4. Respond to the oldest unread email:
```bash
python email_client.py --respond
```

5. Check and summarize in one command:
```bash
python email_client.py --check --summarize
```
# command-center
# command-center
