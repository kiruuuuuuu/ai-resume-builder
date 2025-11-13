"""
Management command to update Django Site model domain from environment variables.
This command is automatically run during Railway deployment.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Update Django Site model domain from RAILWAY_PUBLIC_DOMAIN environment variable'

    def handle(self, *args, **options):
        try:
            # Get domain from environment variable
            # Railway provides RAILWAY_PUBLIC_DOMAIN or we can use RAILWAY_STATIC_URL
            railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            
            # Fallback to common Railway domain pattern if not set
            # Check if we're on Railway by looking for Railway-specific env vars
            if not railway_domain:
                # Try to get from SITE_DOMAIN environment variable
                railway_domain = os.getenv('SITE_DOMAIN')
                
            # If still not set, use the known production domain
            if not railway_domain:
                railway_domain = 'ai-resume-builder-jk.up.railway.app'
            
            # Remove protocol if present
            if railway_domain.startswith('http://'):
                railway_domain = railway_domain.replace('http://', '')
            if railway_domain.startswith('https://'):
                railway_domain = railway_domain.replace('https://', '')
            
            # Remove trailing slash
            railway_domain = railway_domain.rstrip('/')
            
            # Get or create Site (usually ID=1)
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': railway_domain,
                    'name': 'AI Resume Builder'
                }
            )
            
            # Update if domain changed
            if site.domain != railway_domain:
                site.domain = railway_domain
                site.name = 'AI Resume Builder'
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Site domain updated: {site.domain}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Site domain already correct: {site.domain}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ Could not update Site domain: {str(e)}. Continuing...'
                )
            )
            # Don't raise exception - allow deployment to continue

