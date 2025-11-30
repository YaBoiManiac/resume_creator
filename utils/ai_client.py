"""AI client for OpenAI API integration."""
import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class AIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def generate_about_me(
        self,
        personal_info: Dict[str, str],
        job_experience: List[Dict[str, Any]],
        job_description: str,
        skills: List[str] = None,
        interests: List[str] = None
    ) -> str:
        """
        Generate a tailored 'About Me' section based on user data and job description.
        
        Args:
            personal_info: Dictionary containing personal information
            job_experience: List of job experience dictionaries
            job_description: The target job description
            skills: Optional list of user skills
            interests: Optional list of interests and background
            
        Returns:
            Generated 'About Me' text
        """
        # Build context about the user
        experience_summary = self._summarize_experience(job_experience)
        skills_text = ", ".join(skills) if skills else "various professional skills"
        interests_text = "\n".join([f"- {interest}" for interest in interests]) if interests else "Not provided"
        
        prompt = f"""Write a professional summary for a resume. The candidate is applying to this role:

{job_description}

Candidate's Background:
{experience_summary}

Key Skills: {skills_text}

Additional Background/Interests:
{interests_text}

Write a 3-4 sentence professional summary that highlights relevant experience and skills for this role. If any interests or background align with the role, mention them naturally. Be specific and genuine. Avoid clichés and corporate jargon. Keep it natural and straightforward.

IMPORTANT: Never use em dashes (—) and avoid contrast phrases like "not only...but also" or "while...also".

Generate only the summary text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer who creates compelling, ATS-optimized professional summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Error generating 'About Me' section: {str(e)}")
    
    def select_relevant_jobs(
        self,
        job_experience: List[Dict[str, Any]],
        job_description: str,
        max_jobs: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Select and rank the most relevant job experiences for the target position.
        Ensures the most recent job is always included.
        
        Args:
            job_experience: List of all job experiences
            job_description: The target job description
            max_jobs: Maximum number of jobs to return
            
        Returns:
            List of relevant job experiences with relevance scores
        """
        if not job_experience:
            return []
        
        # Find the most recent job based on end_date
        most_recent_job = None
        most_recent_index = -1
        
        for i, job in enumerate(job_experience):
            end_date = job.get('end_date', '')
            if end_date.lower() == 'present':
                most_recent_job = job
                most_recent_index = i
                break
            # If no 'Present', find the latest year
            if not most_recent_job or (end_date and end_date > job_experience[most_recent_index].get('end_date', '')):
                most_recent_job = job
                most_recent_index = i
        
        # Build prompt for job selection
        jobs_text = ""
        for i, job in enumerate(job_experience):
            jobs_text += f"\nJob {i + 1}:\n"
            jobs_text += f"- Title: {job.get('title', 'N/A')}\n"
            jobs_text += f"- Company: {job.get('company', 'N/A')}\n"
            jobs_text += f"- Position: {job.get('position', 'N/A')}\n"
            jobs_text += f"- Duration: {job.get('start_date', 'N/A')} to {job.get('end_date', 'N/A')}\n"
            jobs_text += f"- Duties: {', '.join(job.get('duties', []))[:200]}...\n"
        
        prompt = f"""You are a resume optimization expert. Analyze each job experience and rank them by relevance to THIS SPECIFIC job posting.

User's Job Experience:
{jobs_text}

TARGET JOB DESCRIPTION (ANALYZE CAREFULLY):
{job_description}

CRITICAL ANALYSIS CRITERIA:
1. Skills Match: How closely do the job's responsibilities match the required skills?
2. Industry Alignment: Is it the same or related industry?
3. Role Similarity: How similar is the job title and level to the target position?
4. Technical Requirements: Does the experience include relevant tools, technologies, or methodologies mentioned in the job posting?
5. Impact Potential: Which experiences best demonstrate the qualifications this employer is seeking?

Instructions:
- Thoroughly analyze the job description to understand what the employer values most
- Rank ALL jobs by relevance (1 being most relevant to THIS specific job posting)
- Prioritize experiences that demonstrate the EXACT skills and qualifications mentioned
- Consider transferable skills that align with the job requirements
- Return only a JSON array of job numbers in order of relevance, like: [2, 1, 4, 3, 5]
- Include all jobs in your ranking
- Return ONLY the JSON array, no other text"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing job relevance for resume optimization. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=100
            )
            
            # Parse the response to get job rankings
            import json
            ranking_text = response.choices[0].message.content.strip()
            rankings = json.loads(ranking_text)
            
            # Return jobs in order of relevance, up to max_jobs
            relevant_jobs = []
            
            # Always include the most recent job first if it's not in the top rankings
            if most_recent_job and (most_recent_index + 1) not in rankings[:max_jobs]:
                relevant_jobs.append(most_recent_job)
                slots_remaining = max_jobs - 1
            else:
                slots_remaining = max_jobs
            
            # Add jobs from ranking
            for rank in rankings:
                if len(relevant_jobs) >= max_jobs:
                    break
                if 1 <= rank <= len(job_experience):
                    job = job_experience[rank - 1]
                    # Don't add most recent job twice
                    if job != most_recent_job:
                        relevant_jobs.append(job)
            
            # If most recent job is in the rankings but not first, reorder to put it first
            if most_recent_job in relevant_jobs and relevant_jobs[0] != most_recent_job:
                relevant_jobs.remove(most_recent_job)
                relevant_jobs.insert(0, most_recent_job)
            
            return relevant_jobs[:max_jobs]
        
        except Exception as e:
            # Fallback: return first max_jobs if AI selection fails
            print(f"Warning: Could not rank jobs with AI ({str(e)}). Using all jobs.")
            return job_experience[:max_jobs]
    
    def highlight_relevant_duties(
        self,
        job: Dict[str, Any],
        job_description: str,
        max_duties: int = 5
    ) -> List[str]:
        """
        Select and enhance the most relevant duties for a specific job experience.
        
        Args:
            job: Single job experience dictionary
            job_description: The target job description
            max_duties: Maximum number of duties to return
            
        Returns:
            List of enhanced, relevant duty descriptions
        """
        duties = job.get('duties', [])
        achievements = job.get('achievements', [])
        
        if not duties:
            return []
        
        all_points = duties + achievements
        duties_text = "\n".join([f"- {duty}" for duty in all_points])
        
        prompt = f"""Rewrite these job duties to be relevant for this job application:

Job: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}

Current Duties:
{duties_text}

Target Job:
{job_description}

Select the {max_duties} most relevant duties and rewrite them to:
- Be specific and quantifiable where possible
- Show real impact and results
- Use clear, direct language
- Match terminology from the job posting naturally

IMPORTANT: Never use em dashes (—) and avoid contrast phrases like "not only...but also".

Return only the bullet points, one per line, starting with "•"."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer who creates impactful, ATS-optimized bullet points."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=400
            )
            
            # Parse the response into a list
            enhanced_text = response.choices[0].message.content.strip()
            enhanced_duties = [
                line.strip().lstrip('•').lstrip('-').strip()
                for line in enhanced_text.split('\n')
                if line.strip() and (line.strip().startswith('•') or line.strip().startswith('-'))
            ]
            
            return enhanced_duties[:max_duties]
        
        except Exception as e:
            # Fallback: return original duties
            print(f"Warning: Could not enhance duties with AI ({str(e)}). Using original duties.")
            return duties[:max_duties]
    
    def _summarize_experience(self, job_experience: List[Dict[str, Any]]) -> str:
        """Create a brief summary of work experience."""
        if not job_experience:
            return "No work experience provided"
        
        summary_parts = []
        for job in job_experience[:3]:  # Only summarize top 3 jobs
            title = job.get('title', 'N/A')
            company = job.get('company', 'N/A')
            duration = f"{job.get('start_date', 'N/A')} to {job.get('end_date', 'N/A')}"
            summary_parts.append(f"- {title} at {company} ({duration})")
        
        return "\n".join(summary_parts)
    
    def generate_tailored_skills(
        self,
        user_skills: List[str],
        job_experience: List[Dict[str, Any]],
        job_description: str,
        max_skills: int = 15
    ) -> List[str]:
        """
        Generate a tailored skills list based on the job description.
        
        Args:
            user_skills: User's current skills list
            job_experience: User's job experience (for additional context)
            job_description: The target job description
            max_skills: Maximum number of skills to return
            
        Returns:
            List of tailored skills prioritized for the job
        """
        # Build context from job experience
        experience_skills = []
        for job in job_experience[:3]:
            duties = job.get('duties', [])
            experience_skills.extend(duties[:2])
        
        experience_context = "\n".join([f"- {skill}" for skill in experience_skills[:5]])
        
        user_skills_text = "\n".join([f"- {skill}" for skill in user_skills]) if user_skills else "Not provided"
        
        prompt = f"""You are a resume optimization expert. Create a tailored skills section for this specific job posting.

User's Current Skills:
{user_skills_text}

User's Experience Context:
{experience_context}

TARGET JOB DESCRIPTION (ANALYZE CAREFULLY):
{job_description}

CRITICAL INSTRUCTIONS:
1. Analyze the job description to identify:
   - Technical skills explicitly mentioned
   - Tools, platforms, and technologies required
   - Soft skills and competencies valued
   - Industry-specific terminology

2. From the user's skills and experience:
   - Select skills that directly match the job requirements
   - Prioritize skills mentioned in the job description
   - Include both technical and soft skills
   - Add inferred skills based on their experience that match the job

3. Return exactly {max_skills} skills:
   - List them in order of relevance to the job posting
   - Use the exact terminology from the job description when possible
   - Keep skill names concise (1-4 words each)
   - Mix technical and soft skills appropriately for the role
   - Ensure all skills are realistic based on their experience

4. Format:
   - Return ONLY a comma-separated list of skills
   - No bullet points, no numbering, no explanations
   - Example: "Python, JavaScript, Team Leadership, API Development, Problem Solving"

Return only the skills list, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating tailored, ATS-optimized skills sections for resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_completion_tokens=200
            )
            
            # Parse the response into a list
            skills_text = response.choices[0].message.content.strip()
            tailored_skills = [skill.strip() for skill in skills_text.split(',')]
            
            return tailored_skills[:max_skills]
        
        except Exception as e:
            # Fallback: return user's original skills
            print(f"Warning: Could not generate tailored skills ({str(e)}). Using original skills.")
            return user_skills[:max_skills]
    
    def generate_cover_letter(
        self,
        personal_info: Dict[str, str],
        job_experience: List[Dict[str, Any]],
        job_description: str,
        company_name: str = None,
        skills: List[str] = None,
        interests: List[str] = None
    ) -> str:
        """
        Generate a personalized cover letter for the job posting.
        
        Args:
            personal_info: Dictionary containing personal information
            job_experience: List of job experience dictionaries
            job_description: The target job description
            company_name: Optional company name
            skills: Optional list of user skills
            interests: Optional list of interests and background
            
        Returns:
            Generated cover letter text
        """
        experience_summary = self._summarize_experience(job_experience)
        skills_text = ", ".join(skills[:5]) if skills else "various professional skills"
        interests_text = "\n".join([f"- {interest}" for interest in interests]) if interests else "Not provided"
        
        # Try to extract company name from job description if not provided
        if not company_name:
            company_name = "your organization"
        
        prompt = f"""Write a cover letter for this job application.

Candidate: {personal_info.get('name', 'N/A')}
Experience: {experience_summary}
Skills: {skills_text}

Background/Interests:
{interests_text}

Job Description:
{job_description}

Write a genuine cover letter (3-4 paragraphs) that:
- Opens naturally
- Connects relevant experience to the role
- Mentions 2-3 specific accomplishments
- Weaves in relevant interests or background if they align with the role
- Closes with interest in the position

Use first person. Be professional but conversational. Avoid clichés and formulaic openings.

IMPORTANT: Never use em dashes (—) and avoid contrast phrases like "not only...but also".

Generate only the letter body (no address, date, or subject line)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing genuine, human-sounding cover letters that avoid AI detection and clichés."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_completion_tokens=600
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Error generating cover letter: {str(e)}")
