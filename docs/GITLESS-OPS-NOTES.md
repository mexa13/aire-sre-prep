# GitLess Ops — prep notes

**Intent:** capture how AI-assisted change might bypass the classic “PR + review + CI” loop, and what **evidence** you still need for production.

## Questions to answer before the course

1. Which changes must still land in Git for audit (Terraform, K8s, policy)?  
2. Where would you store **signed prompts / agent plans** if not in Git?  
3. How do you detect **drift** between cluster state and declared intent without full GitOps?  
4. What CI checks remain non-negotiable (security scans, policy tests)?  

## Your stance (fill in)

- **Comfortable automating:**  
- **Never without human gate:**  
- **Open questions for mentor:** (also see [MENTOR-QUESTIONS.md](MENTOR-QUESTIONS.md))
