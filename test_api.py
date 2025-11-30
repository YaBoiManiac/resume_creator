"""Test script to verify AI client and data handler functionality."""
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from utils.data_handler import load_data, validate_data
from utils.ai_client import AIClient
from utils.resume_builder import ResumeBuilder


console = Console()


def test_data_handler():
    """Test data loading and validation."""
    console.print(Panel.fit("📂 Testing Data Handler", style="bold cyan"))
    
    try:
        # Load data
        console.print("\n[yellow]Loading user data...[/yellow]")
        data = load_data()
        
        # Check if data exists
        if not data['personal_info']['name']:
            console.print("[red]❌ No user data found![/red]")
            console.print("[yellow]Please run 'python collect_info.py' first to create your profile.[/yellow]")
            return None
        
        # Validate data
        console.print("[yellow]Validating data structure...[/yellow]")
        if validate_data(data):
            console.print("[green]✓ Data structure is valid[/green]")
        else:
            console.print("[red]❌ Data structure is invalid[/red]")
            return None
        
        # Display summary
        console.print(f"\n[bold]Personal Info:[/bold]")
        console.print(f"  Name: {data['personal_info']['name']}")
        console.print(f"  Email: {data['personal_info']['email']}")
        console.print(f"\n[bold]Job Experience:[/bold] {len(data['job_experience'])} jobs found")
        
        for i, job in enumerate(data['job_experience'][:3], 1):
            console.print(f"  {i}. {job['title']} at {job['company']}")
        
        if data.get('skills'):
            console.print(f"\n[bold]Skills:[/bold] {len(data['skills'])} skills")
        
        console.print("\n[green]✓ Data handler test passed![/green]")
        return data
        
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        return None


def test_ai_client(data):
    """Test AI client functionality."""
    console.print("\n" + "="*60)
    console.print(Panel.fit("🤖 Testing AI Client", style="bold cyan"))
    
    try:
        # Initialize AI client
        console.print("\n[yellow]Initializing AI client...[/yellow]")
        ai_client = AIClient()
        console.print(f"[green]✓ AI client initialized (using {ai_client.model})[/green]")
        
        # Sample job description for testing
        sample_job_description = """
        Senior Software Engineer
        
        We are seeking an experienced software engineer to join our team. 
        The ideal candidate will have:
        - 5+ years of experience in software development
        - Strong programming skills in Python and JavaScript
        - Experience with web applications and APIs
        - Excellent problem-solving abilities
        - Strong communication and teamwork skills
        
        Responsibilities:
        - Design and develop scalable applications
        - Collaborate with cross-functional teams
        - Write clean, maintainable code
        - Mentor junior developers
        """
        
        console.print("\n[bold]Using sample job description:[/bold]")
        console.print("[dim]" + sample_job_description.strip()[:150] + "...[/dim]")
        
        # Test 1: Generate About Me
        console.print("\n[yellow]Test 1: Generating 'About Me' section...[/yellow]")
        about_me = ai_client.generate_about_me(
            personal_info=data['personal_info'],
            job_experience=data['job_experience'],
            job_description=sample_job_description,
            skills=data.get('skills', [])
        )
        console.print("[green]✓ Successfully generated 'About Me' section[/green]")
        console.print(Panel(about_me, title="Generated About Me", border_style="green"))
        
        # Test 2: Select Relevant Jobs
        if data['job_experience']:
            console.print("\n[yellow]Test 2: Selecting relevant job experiences...[/yellow]")
            relevant_jobs = ai_client.select_relevant_jobs(
                job_experience=data['job_experience'],
                job_description=sample_job_description,
                max_jobs=3
            )
            console.print(f"[green]✓ Selected {len(relevant_jobs)} most relevant jobs[/green]")
            
            for i, job in enumerate(relevant_jobs, 1):
                console.print(f"  {i}. {job['title']} at {job['company']}")
            
            # Test 3: Highlight Relevant Duties
            if relevant_jobs:
                console.print("\n[yellow]Test 3: Enhancing duties for most relevant job...[/yellow]")
                enhanced_duties = ai_client.highlight_relevant_duties(
                    job=relevant_jobs[0],
                    job_description=sample_job_description,
                    max_duties=3
                )
                console.print(f"[green]✓ Generated {len(enhanced_duties)} enhanced duties[/green]")
                console.print(Panel(
                    "\n".join([f"• {duty}" for duty in enhanced_duties]),
                    title=f"Enhanced Duties - {relevant_jobs[0]['title']}",
                    border_style="green"
                ))
                
                # Test 4: Build complete resume
                console.print("\n[yellow]Test 4: Building complete DOCX resume...[/yellow]")
                
                # Collect all enhanced duties for relevant jobs
                enhanced_duties_dict = {}
                for idx, job in enumerate(relevant_jobs[:3]):
                    duties = ai_client.highlight_relevant_duties(
                        job=job,
                        job_description=sample_job_description,
                        max_duties=4
                    )
                    enhanced_duties_dict[idx] = duties
                
                # Build the resume
                builder = ResumeBuilder()
                output_path = builder.build_complete_resume(
                    personal_info=data['personal_info'],
                    about_me=about_me,
                    jobs=relevant_jobs[:3],
                    enhanced_duties=enhanced_duties_dict,
                    education=data.get('education', []),
                    skills=data.get('skills', []),
                    certifications=data.get('certifications', []),
                    filename="test_resume"
                )
                
                console.print(f"[green]✓ Resume successfully created![/green]")
                console.print(f"[bold cyan]📄 Resume saved to: {output_path}[/bold cyan]")
        
        console.print("\n[bold green]✓ All tests passed![/bold green]")
        console.print("\n[cyan]The AI integration and resume builder are working correctly![/cyan]")
        
    except ValueError as e:
        console.print(f"\n[red]❌ Configuration Error: {str(e)}[/red]")
        console.print("\n[yellow]Please check your .env file and ensure OPENAI_API_KEY is set correctly.[/yellow]")
        
    except Exception as e:
        console.print(f"\n[red]❌ AI Client Error: {str(e)}[/red]")
        console.print("\n[yellow]This might be an API issue. Check your API key and internet connection.[/yellow]")


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold cyan]AI Client & Data Handler Test Suite[/bold cyan]\n"
        "Testing core functionality before building the resume generator",
        style="bold"
    ))
    
    # Test data handler
    data = test_data_handler()
    
    if data is None:
        console.print("\n[red]Tests aborted due to data handler failure.[/red]")
        return
    
    # Test AI client
    test_ai_client(data)
    
    console.print("\n" + "="*60)
    console.print("[bold green]Test suite complete![/bold green]")
    console.print("\n[cyan]✓ Check the 'output/' folder for your test resume[/cyan]")
    console.print("[cyan]✓ Next step: Run 'python generate_resume.py' to create custom resumes for real job postings[/cyan]")


if __name__ == "__main__":
    main()
