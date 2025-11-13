"""
Django management command to check OAuth configuration.
This helps diagnose OAuth setup issues.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Check OAuth configuration and diagnose issues'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== OAuth Configuration Check ===\n'))
        
        # Check Django Site Model
        try:
            site = Site.objects.get(id=1)
            self.stdout.write(f'✅ Site Model:')
            self.stdout.write(f'   Domain: {site.domain}')
            self.stdout.write(f'   Name: {site.name}')
            
            # Check if domain matches expected
            expected_domain = 'ai-resume-builder-jk.up.railway.app'
            if site.domain != expected_domain:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠️ WARNING: Domain should be "{expected_domain}"'
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'   ✅ Domain matches expected: {expected_domain}'
                ))
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR('   ❌ Site model not found!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
        
        self.stdout.write('')
        
        # Check Google OAuth Configuration
        self.stdout.write('🔍 Google OAuth Configuration:')
        google_client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '')
        google_client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', '')
        
        if not google_client_id:
            self.stdout.write(self.style.ERROR('   ❌ GOOGLE_OAUTH2_CLIENT_ID is NOT set'))
            self.stdout.write(self.style.WARNING('   → Set it in Railway Variables'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ GOOGLE_OAUTH2_CLIENT_ID is set'))
            self.stdout.write(f'      Value: {google_client_id[:20]}...' if len(google_client_id) > 20 else f'      Value: {google_client_id}')
            
            # Check Client ID format
            if not google_client_id.startswith(('http://', 'https://')):
                self.stdout.write(self.style.SUCCESS('   ✅ No http:// or https:// prefix (correct)'))
            else:
                self.stdout.write(self.style.ERROR('   ❌ Client ID has http:// or https:// prefix (WRONG!)'))
            
            # Check if Client ID looks complete
            if google_client_id.count('-') >= 1 and '.apps.googleusercontent.com' in google_client_id:
                self.stdout.write(self.style.SUCCESS('   ✅ Client ID format looks correct'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️ Client ID format might be incomplete'))
                self.stdout.write(self.style.WARNING('   → Should end with .apps.googleusercontent.com'))
        
        if not google_client_secret:
            self.stdout.write(self.style.ERROR('   ❌ GOOGLE_OAUTH2_CLIENT_SECRET is NOT set'))
            self.stdout.write(self.style.WARNING('   → Set it in Railway Variables'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ GOOGLE_OAUTH2_CLIENT_SECRET is set'))
            self.stdout.write(f'      Length: {len(google_client_secret)} characters')
        
        # Check settings.py configuration
        self.stdout.write('')
        self.stdout.write('🔍 Django Settings Configuration:')
        if hasattr(settings, 'SOCIALACCOUNT_PROVIDERS'):
            google_config = settings.SOCIALACCOUNT_PROVIDERS.get('google', {})
            app_config = google_config.get('APP', {})
            client_id_from_settings = app_config.get('client_id', '')
            
            if client_id_from_settings:
                self.stdout.write(self.style.SUCCESS('   ✅ Google OAuth configured in settings'))
                if client_id_from_settings == google_client_id:
                    self.stdout.write(self.style.SUCCESS('   ✅ Client ID matches environment variable'))
                else:
                    self.stdout.write(self.style.WARNING('   ⚠️ Client ID mismatch between settings and env var'))
            else:
                self.stdout.write(self.style.ERROR('   ❌ Google OAuth not configured in settings'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ SOCIALACCOUNT_PROVIDERS not found in settings'))
        
        self.stdout.write('')
        
        # Check GitHub OAuth Configuration
        self.stdout.write('🔍 GitHub OAuth Configuration:')
        github_client_id = os.getenv('GITHUB_CLIENT_ID', '')
        github_client_secret = os.getenv('GITHUB_CLIENT_SECRET', '')
        
        if not github_client_id:
            self.stdout.write(self.style.WARNING('   ⚠️ GITHUB_CLIENT_ID is NOT set'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ GITHUB_CLIENT_ID is set'))
            self.stdout.write(f'      Value: {github_client_id[:20]}...' if len(github_client_id) > 20 else f'      Value: {github_client_id}')
        
        if not github_client_secret:
            self.stdout.write(self.style.WARNING('   ⚠️ GITHUB_CLIENT_SECRET is NOT set'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ GITHUB_CLIENT_SECRET is set'))
        
        self.stdout.write('')
        
        # Expected Redirect URIs
        self.stdout.write('🔍 Expected Redirect URIs:')
        site_domain = Site.objects.get(id=1).domain if Site.objects.filter(id=1).exists() else 'ai-resume-builder-jk.up.railway.app'
        google_redirect_uri = f'https://{site_domain}/accounts/google/login/callback/'
        github_redirect_uri = f'https://{site_domain}/accounts/github/login/callback/'
        
        self.stdout.write(f'   Google: {google_redirect_uri}')
        self.stdout.write(f'   GitHub: {github_redirect_uri}')
        
        self.stdout.write('')
        self.stdout.write('=== Summary ===')
        
        # Overall status
        issues = []
        if not google_client_id:
            issues.append('Google Client ID not set')
        if not google_client_secret:
            issues.append('Google Client Secret not set')
        
        if issues:
            self.stdout.write(self.style.ERROR(f'❌ Issues found: {", ".join(issues)}'))
            self.stdout.write('')
            self.stdout.write('🔧 Fix Steps:')
            self.stdout.write('1. Go to Google Cloud Console → APIs & Services → Credentials')
            self.stdout.write('2. Find your OAuth 2.0 Client ID')
            self.stdout.write('3. Copy the complete Client ID and Client Secret')
            self.stdout.write('4. Add to Railway Dashboard → Variables:')
            self.stdout.write('   - GOOGLE_OAUTH2_CLIENT_ID')
            self.stdout.write('   - GOOGLE_OAUTH2_CLIENT_SECRET')
            self.stdout.write('5. Make sure redirect URI is added in Google Cloud Console:')
            self.stdout.write(f'   {google_redirect_uri}')
        else:
            self.stdout.write(self.style.SUCCESS('✅ All OAuth variables are set'))
            self.stdout.write('')
            self.stdout.write('⚠️ If Google OAuth still doesn\'t work:')
            self.stdout.write('1. Verify redirect URI in Google Cloud Console matches exactly:')
            self.stdout.write(f'   {google_redirect_uri}')
            self.stdout.write('2. Make sure Client ID in Railway matches Google Cloud Console exactly')
            self.stdout.write('3. Check that OAuth client is enabled (not deleted) in Google Cloud Console')
            self.stdout.write('4. Wait 2-3 minutes after updating Railway variables')
            self.stdout.write('5. Clear browser cache and try again')

