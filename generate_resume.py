"""Resume generator - Creates tailored resumes from job descriptions."""
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from utils.data_handler import load_data
from utils.ai_client import AIClient
from utils.resume_builder import ResumeBuilder
from utils.cover_letter_builder import CoverLetterBuilder
import sys


console = Console()


def get_job_description() -> str:
    """Get job description from user via multiline input."""
    console.print(Panel.fit("📋 Job Description Input", style="bold cyan"))
    
    console.print("\n[yellow]Paste the job description below.[/yellow]")
    console.print("[dim]When finished, press Enter on an empty line twice.[/dim]\n")
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if not line.strip():
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    
    job_description = "\n".join(lines).strip()
    
    if not job_description:
        console.print("[red]No job description provided.[/red]")
        return None
    
    console.print(f"\n[green]✓ Job description received ({len(job_description)} characters)[/green]")
    return job_description


def format_date_year_only(date_str: str) -> str:
    """Convert YYYY-MM date to just YYYY."""
    if not date_str or date_str.lower() == 'present':
        return date_str
    
    # Extract just the year (first 4 characters)
    if '-' in date_str:
        return date_str.split('-')[0]
    return date_str


def generate_resume(data: dict, job_description: str, ai_client: AIClient) -> dict:
    """
    Generate a tailored resume using AI.
    
    Returns a dictionary with all resume components.
    """
    resume_data = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Generate About Me
        task1 = progress.add_task("[cyan]Generating professional summary...", total=None)
        about_me = ai_client.generate_about_me(
            personal_info=data['personal_info'],
            job_experience=data['job_experience'],
            job_description=job_description,
            skills=data.get('skills', []),
            interests=data.get('interests_and_background', [])
        )
        progress.update(task1, completed=True)
        resume_data['about_me'] = about_me
        
        # Step 2: Select relevant jobs
        task2 = progress.add_task("[cyan]Analyzing and ranking job experiences...", total=None)
        relevant_jobs = ai_client.select_relevant_jobs(
            job_experience=data['job_experience'],
            job_description=job_description,
            max_jobs=3
        )
        progress.update(task2, completed=True)
        
        # Format dates to year only
        for job in relevant_jobs:
            job['start_date'] = format_date_year_only(job['start_date'])
            job['end_date'] = format_date_year_only(job['end_date'])
        
        resume_data['jobs'] = relevant_jobs
        
        # Step 3: Generate tailored duties for each job
        task3 = progress.add_task(f"[cyan]Enhancing duties for {len(relevant_jobs)} jobs...", total=None)
        enhanced_duties = {}
        for idx, job in enumerate(relevant_jobs):
            duties = ai_client.highlight_relevant_duties(
                job=job,
                job_description=job_description,
                max_duties=5
            )
            enhanced_duties[idx] = duties
        progress.update(task3, completed=True)
        resume_data['enhanced_duties'] = enhanced_duties
        
        # Step 4: Generate tailored skills list
        task4 = progress.add_task("[cyan]Selecting relevant skills...", total=None)
        tailored_skills = ai_client.generate_tailored_skills(
            user_skills=data.get('skills', []),
            job_experience=data['job_experience'],
            job_description=job_description
        )
        progress.update(task4, completed=True)
        resume_data['skills'] = tailored_skills
        
        # Step 5: Generate cover letter
        task5 = progress.add_task("[cyan]Writing cover letter...", total=None)
        cover_letter = ai_client.generate_cover_letter(
            personal_info=data['personal_info'],
            job_experience=data['job_experience'],
            job_description=job_description,
            skills=tailored_skills,
            interests=data.get('interests_and_background', [])
        )
        progress.update(task5, completed=True)
        resume_data['cover_letter'] = cover_letter
    
    console.print("\n[bold green]✓ Resume and cover letter generated successfully![/bold green]")
    return resume_data


def display_preview(data: dict, resume_data: dict):
    """Display a preview of the generated resume."""
    console.print("\n" + "="*70)
    console.print(Panel.fit("📄 Resume Preview", style="bold green"))
    
    # Header
    console.print(f"\n[bold cyan]{data['personal_info']['name']}[/bold cyan]")
    contact = f"{data['personal_info']['email']} | {data['personal_info']['phone']}"
    console.print(f"[dim]{contact}[/dim]")
    
    # About Me
    console.print(f"\n[bold]PROFESSIONAL SUMMARY[/bold]")
    console.print(resume_data['about_me'])
    
    # Experience
    console.print(f"\n[bold]PROFESSIONAL EXPERIENCE[/bold]")
    for idx, job in enumerate(resume_data['jobs'][:3]):
        console.print(f"\n[cyan]{job['title']} | {job['company']}[/cyan]")
        console.print(f"[dim]{job['start_date']} - {job['end_date']}[/dim]")
        
        duties = resume_data['enhanced_duties'].get(idx, [])
        for duty in duties[:3]:
            console.print(f"  • {duty}")
        
        if len(duties) > 3:
            console.print(f"  [dim]... and {len(duties) - 3} more[/dim]")
    
    if len(resume_data['jobs']) > 3:
        console.print(f"\n[dim]... and {len(resume_data['jobs']) - 3} more jobs[/dim]")
    
    # Skills
    if resume_data.get('skills'):
        console.print(f"\n[bold]SKILLS[/bold]")
        console.print(" • ".join(resume_data['skills'][:10]))
        if len(resume_data['skills']) > 10:
            console.print(f"[dim]... and {len(resume_data['skills']) - 10} more[/dim]")
    
    # Education
    if data.get('education'):
        console.print(f"\n[bold]EDUCATION[/bold]")
        for edu in data['education'][:2]:
            console.print(f"  {edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})")
    
    console.print("\n" + "="*70)


def save_documents(data: dict, resume_data: dict, custom_filename: str = None) -> tuple:
    """Build and save both resume and cover letter as DOCX files, plus raw text versions."""
    console.print("\n[yellow]Building documents...[/yellow]")
    
    from pathlib import Path
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Determine base filename
    if not custom_filename:
        from datetime import datetime
        custom_filename = datetime.now().strftime("resume_%Y%m%d_%H%M%S")
    
    # Build resume
    resume_builder = ResumeBuilder()
    resume_path = resume_builder.build_complete_resume(
        personal_info=data['personal_info'],
        about_me=resume_data['about_me'],
        jobs=resume_data['jobs'],
        enhanced_duties=resume_data['enhanced_duties'],
        education=data.get('education', []),
        skills=resume_data['skills'],
        certifications=data.get('certifications', []),
        filename=custom_filename
    )
    
    # Build cover letter
    cover_letter_builder = CoverLetterBuilder()
    cover_letter_path = cover_letter_builder.build_complete_cover_letter(
        personal_info=data['personal_info'],
        cover_letter_text=resume_data['cover_letter'],
        filename=custom_filename
    )
    
    # Save raw text versions
    resume_raw_path = output_dir / f"{custom_filename}_raw.txt"
    cover_letter_raw_path = output_dir / f"{custom_filename}_cover_letter_raw.txt"
    
    # Build raw resume text
    raw_resume_text = f"""{data['personal_info']['name']}
{data['personal_info']['email']} | {data['personal_info']['phone']}

PROFESSIONAL SUMMARY
{resume_data['about_me']}

PROFESSIONAL EXPERIENCE
"""
    
    for idx, job in enumerate(resume_data['jobs']):
        raw_resume_text += f"\n{job['title']} | {job['company']}\n"
        raw_resume_text += f"{job['start_date']} - {job['end_date']}\n"
        duties = resume_data['enhanced_duties'].get(idx, [])
        for duty in duties:
            raw_resume_text += f"• {duty}\n"
    
    if data.get('education'):
        raw_resume_text += "\nEDUCATION\n"
        for edu in data['education']:
            raw_resume_text += f"{edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})\n"
    
    if resume_data.get('skills'):
        raw_resume_text += f"\nSKILLS\n{' • '.join(resume_data['skills'])}\n"
    
    # Save raw files
    with open(resume_raw_path, 'w', encoding='utf-8') as f:
        f.write(raw_resume_text)
    
    with open(cover_letter_raw_path, 'w', encoding='utf-8') as f:
        f.write(resume_data['cover_letter'])
    
    return resume_path, cover_letter_path, resume_raw_path, cover_letter_raw_path


def main():
    """Main function to run the resume generator."""
    console.print(Panel.fit(
        "[bold cyan]Resume Generator[/bold cyan]\n"
        "Create tailored resumes from job descriptions using AI",
        style="bold"
    ))
    
    try:
        # Load user data
        console.print("\n[yellow]Loading your profile data...[/yellow]")
        data = load_data()
        
        if not data['personal_info']['name']:
            console.print("[red]❌ No user data found![/red]")
            console.print("[yellow]Please run 'python collect_info.py' first to create your profile.[/yellow]")
            return
        
        console.print(f"[green]✓ Profile loaded: {data['personal_info']['name']}[/green]")
        console.print(f"[dim]  {len(data['job_experience'])} jobs, {len(data.get('skills', []))} skills[/dim]")
        
        # Get job description
        console.print("\n")
        job_description = get_job_description()
        
        if not job_description:
            console.print("[red]Cancelled.[/red]")
            return
        
        # Initialize AI client
        console.print("\n[yellow]Initializing AI...[/yellow]")
        ai_client = AIClient()
        console.print(f"[green]✓ AI client ready (using {ai_client.model})[/green]")
        
        # Generate resume
        console.print("\n")
        resume_data = generate_resume(data, job_description, ai_client)
        
        # Display preview
        display_preview(data, resume_data)
        
        # Preview cover letter
        console.print("\n" + "="*70)
        console.print(Panel.fit("📝 Cover Letter Preview", style="bold green"))
        console.print("\n" + resume_data['cover_letter'][:500] + "...")
        console.print("\n" + "="*70)
        
        # Ask to save
        console.print("\n")
        if not Confirm.ask("Save resume and cover letter?", default=True):
            console.print("[yellow]Documents not saved.[/yellow]")
            return
        
        # Get custom filename
        custom_name = Prompt.ask(
            "\nEnter a base filename (optional, press Enter for auto-generated name)",
            default=""
        )
        
        filename = custom_name if custom_name else None
        
        # Save both documents
        resume_path, cover_letter_path, resume_raw_path, cover_letter_raw_path = save_documents(data, resume_data, filename)
        
        console.print(f"\n[bold green]✓ Documents created successfully![/bold green]")
        console.print(f"[bold cyan]📄 Resume: {resume_path}[/bold cyan]")
        console.print(f"[bold cyan]📝 Cover Letter: {cover_letter_path}[/bold cyan]")
        console.print(f"[dim]📄 Raw Resume: {resume_raw_path}[/dim]")
        console.print(f"[dim]📝 Raw Cover Letter: {cover_letter_raw_path}[/dim]")
        console.print("\n[dim]You can now open these files in Microsoft Word to review and make any final adjustments.[/dim]")
        
    except ValueError as e:
        console.print(f"\n[red]❌ Configuration Error: {str(e)}[/red]")
        console.print("[yellow]Please check your .env file and ensure OPENAI_API_KEY is set correctly.[/yellow]")
        sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
