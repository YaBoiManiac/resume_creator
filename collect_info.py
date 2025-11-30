"""Data collection script for gathering personal information and job experience."""
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from utils.data_handler import load_data, save_data


console = Console()


def collect_personal_info() -> dict:
    """Collect personal information from user."""
    console.print(Panel.fit("📋 Personal Information", style="bold cyan"))
    
    personal_info = {
        "name": Prompt.ask("Full Name"),
        "email": Prompt.ask("Email"),
        "phone": Prompt.ask("Phone Number"),
        "location": Prompt.ask("Location (City, State)"),
        "linkedin": Prompt.ask("LinkedIn URL (optional)", default=""),
        "portfolio": Prompt.ask("Portfolio/Website URL (optional)", default="")
    }
    
    return personal_info


def collect_job_experience() -> list:
    """Collect job experience entries from user."""
    console.print(Panel.fit("💼 Job Experience", style="bold cyan"))
    
    jobs = []
    job_id = 1
    
    while True:
        console.print(f"\n[bold yellow]Job #{job_id}[/bold yellow]")
        
        title = Prompt.ask("Job Title")
        company = Prompt.ask("Company Name")
        position = Prompt.ask("Position/Role")
        start_date = Prompt.ask("Start Date (YYYY-MM)")
        end_date = Prompt.ask("End Date (YYYY-MM or 'Present')")
        
        # Collect duties
        console.print("\n[cyan]Enter job duties/responsibilities (one per line, press Enter on empty line to finish):[/cyan]")
        duties = []
        while True:
            duty = Prompt.ask(f"  Duty #{len(duties) + 1}", default="")
            if not duty:
                break
            duties.append(duty)
        
        # Optional achievements
        console.print("\n[cyan]Enter achievements (optional, press Enter on empty line to finish):[/cyan]")
        achievements = []
        while True:
            achievement = Prompt.ask(f"  Achievement #{len(achievements) + 1}", default="")
            if not achievement:
                break
            achievements.append(achievement)
        
        job = {
            "id": job_id,
            "title": title,
            "company": company,
            "position": position,
            "start_date": start_date,
            "end_date": end_date,
            "duties": duties,
            "achievements": achievements if achievements else []
        }
        
        jobs.append(job)
        
        # Ask if they want to add another job
        if not Confirm.ask("\nAdd another job?", default=False):
            break
        
        job_id += 1
    
    return jobs


def collect_additional_info() -> tuple:
    """Collect education, skills, certifications, and interests."""
    console.print(Panel.fit("🎓 Additional Information (Optional)", style="bold cyan"))
    
    # Education
    education = []
    if Confirm.ask("\nAdd education information?", default=True):
        while True:
            console.print("\n[bold yellow]Education Entry[/bold yellow]")
            degree = Prompt.ask("Degree/Certification")
            institution = Prompt.ask("Institution")
            year = Prompt.ask("Graduation Year")
            
            education.append({
                "degree": degree,
                "institution": institution,
                "year": year
            })
            
            if not Confirm.ask("Add another education entry?", default=False):
                break
    
    # Skills
    skills = []
    if Confirm.ask("\nAdd skills?", default=True):
        console.print("[cyan]Enter skills (one per line, press Enter on empty line to finish):[/cyan]")
        while True:
            skill = Prompt.ask(f"  Skill #{len(skills) + 1}", default="")
            if not skill:
                break
            skills.append(skill)
    
    # Certifications
    certifications = []
    if Confirm.ask("\nAdd certifications?", default=False):
        console.print("[cyan]Enter certifications (one per line, press Enter on empty line to finish):[/cyan]")
        while True:
            cert = Prompt.ask(f"  Certification #{len(certifications) + 1}", default="")
            if not cert:
                break
            certifications.append(cert)
    
    # Interests and Background
    interests = []
    if Confirm.ask("\nAdd interests/background information?", default=False):
        console.print("[cyan]Enter interests, hobbies, or background details that might be relevant:[/cyan]")
        console.print("[dim]E.g., 'Own and maintain motorcycles', 'Build custom PCs', etc.[/dim]")
        while True:
            interest = Prompt.ask(f"  Interest #{len(interests) + 1}", default="")
            if not interest:
                break
            interests.append(interest)
    
    return education, skills, certifications, interests


def display_summary(data: dict) -> None:
    """Display a summary of collected data."""
    console.print("\n" + "="*60)
    console.print(Panel.fit("📊 Data Collection Summary", style="bold green"))
    
    # Personal info
    console.print("\n[bold]Personal Information:[/bold]")
    console.print(f"  Name: {data['personal_info']['name']}")
    console.print(f"  Email: {data['personal_info']['email']}")
    console.print(f"  Phone: {data['personal_info']['phone']}")
    console.print(f"  Location: {data['personal_info']['location']}")
    
    # Job experience
    console.print(f"\n[bold]Job Experience:[/bold] {len(data['job_experience'])} jobs")
    for job in data['job_experience']:
        console.print(f"  • {job['title']} at {job['company']} ({job['start_date']} - {job['end_date']})")
    
    # Education
    if data['education']:
        console.print(f"\n[bold]Education:[/bold] {len(data['education'])} entries")
    
    # Skills
    if data['skills']:
        console.print(f"\n[bold]Skills:[/bold] {len(data['skills'])} skills")
    
    # Certifications
    if data['certifications']:
        console.print(f"\n[bold]Certifications:[/bold] {len(data['certifications'])} certifications")


def main():
    """Main function to run the data collection process."""
    console.print(Panel.fit(
        "[bold cyan]Resume Creator - Data Collection[/bold cyan]\n"
        "Let's gather your information for resume generation",
        style="bold"
    ))
    
    # Load existing data (if any)
    data = load_data()
    
    # Check if data already exists
    if data['personal_info']['name']:
        console.print("\n[yellow]⚠ Existing data found![/yellow]")
        if not Confirm.ask("This will overwrite existing data. Continue?", default=False):
            console.print("[red]Cancelled.[/red]")
            return
    
    # Collect information
    console.print("\n")
    data['personal_info'] = collect_personal_info()
    
    console.print("\n")
    data['job_experience'] = collect_job_experience()
    
    console.print("\n")
    education, skills, certifications, interests = collect_additional_info()
    data['education'] = education
    data['skills'] = skills
    data['certifications'] = certifications
    data['interests_and_background'] = interests
    
    # Display summary
    display_summary(data)
    
    # Confirm and save
    console.print("\n")
    if Confirm.ask("Save this data?", default=True):
        save_data(data)
        console.print("\n[bold green]✓ Data collection complete![/bold green]")
    else:
        console.print("\n[red]Data not saved.[/red]")


if __name__ == "__main__":
    main()
