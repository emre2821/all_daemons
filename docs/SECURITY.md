# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

We take the security of All Daemons seriously. If you believe you have found a security vulnerability, please report it to us responsibly.

### How to Report

1. **Do NOT** disclose the vulnerability publicly until it has been addressed.
2. **Do NOT** open a public GitHub issue for security vulnerabilities.
3. Email your findings or open a private security advisory via [GitHub's Security Advisories](https://github.com/emre2821/all_daemons/security/advisories).

### What to Include

Please include the following information in your report:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes (if you have them)

### Response Timeline

- We will acknowledge your report within **48 hours**
- We will provide a detailed response within **7 days** indicating next steps
- We will notify you when the vulnerability has been fixed

### Safe Harbor

We consider security research conducted in accordance with this policy to be:
- Authorized in view of any applicable anti-hacking laws
- Exempt from restrictions in our Terms of Service that would interfere with conducting security research

We will not pursue civil action or initiate a complaint against you for accidental, good-faith violations of this policy.

## Security Best Practices for Contributors

When contributing to this project, please follow these security practices:

### Code Security

- **Never commit secrets:** API keys, passwords, tokens, or other sensitive data should never be committed to the repository
- **Use environment variables:** Store sensitive configuration in environment variables, not in code
- **Validate input:** Always validate and sanitize user input
- **Keep dependencies updated:** Regularly update dependencies to patch known vulnerabilities

### Environment Variables

We provide a `.env.example` file as a template. Copy it to `.env` and fill in your values:

```bash
cp .env.example .env
```

Never commit your actual `.env` file—it's listed in `.gitignore`.

## Dependency Security

This project uses GitHub's Dependabot to automatically monitor and update dependencies with known vulnerabilities. You can also run manual security checks:

```bash
# For Python dependencies
pip install safety
safety check -r requirements.txt
```

## Thank You

Thank you for helping keep All Daemons and our users safe! 🛡️
