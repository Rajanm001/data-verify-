"""
AI Service for generating negotiation briefs and client emails
Uses OpenAI API with fallback to template-based generation
"""

import os
import time
import hashlib
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
    OpenAIType = OpenAI
    AsyncOpenAIType = AsyncOpenAI
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAIType = None  # type: ignore
    AsyncOpenAIType = None  # type: ignore

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    GroqType = Groq
except ImportError:
    GROQ_AVAILABLE = False
    GroqType = None  # type: ignore

from src.models import ChecklistItem

# Configure professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIMetrics:
    """Advanced metrics tracking for AI service performance"""
    openai_requests: int = 0
    openai_successes: int = 0
    openai_failures: int = 0
    groq_requests: int = 0
    groq_successes: int = 0
    groq_failures: int = 0
    template_fallbacks: int = 0
    total_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    
    @property
    def average_response_time(self) -> float:
        total_requests = self.openai_requests + self.groq_requests
        return self.total_response_time / total_requests if total_requests > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        total_requests = self.openai_requests + self.groq_requests
        total_successes = self.openai_successes + self.groq_successes
        return total_successes / total_requests if total_requests > 0 else 0.0

@dataclass
class CacheEntry:
    """Professional caching system for AI responses"""
    content: str
    timestamp: datetime
    provider: str
    ttl_minutes: int = 15
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() - self.timestamp > timedelta(minutes=self.ttl_minutes)

class EnterpriseAIService:
    """🚀 Professional-grade AI service with multi-provider support, caching, and advanced metrics"""
    
    def __init__(self):
        self.openai_client: Optional[Any] = None
        self.async_openai_client: Optional[Any] = None
        self.groq_client: Optional[Any] = None
        self.use_openai = False
        self.use_groq = False
        
        # Advanced features
        self.metrics = AIMetrics()
        self.cache: Dict[str, CacheEntry] = {}
        self.rate_limiter = self._init_rate_limiter()
        
        # Initialize AI providers with sophisticated error handling
        self._initialize_providers()
        
        logger.info(f"🎯 Enterprise AI Service initialized - Providers: {self._get_provider_status()}")
    
    def _initialize_providers(self) -> None:
        """Initialize AI providers with comprehensive error handling and validation"""
        
        # Priority 1: OpenAI (Premium quality)
        if OPENAI_AVAILABLE and OpenAIType is not None and AsyncOpenAIType is not None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and self._validate_api_key(api_key, "openai"):
                try:
                    self.openai_client = OpenAIType(api_key=api_key)
                    self.async_openai_client = AsyncOpenAIType(api_key=api_key)
                    self.use_openai = True
                    logger.info("🔥 OpenAI GPT-4 client initialized (Enterprise Primary)")
                except Exception as e:
                    logger.warning(f"⚠️ OpenAI initialization failed: {e}")
                    self.use_openai = False
        
        # Priority 2: GROQ (High-speed fallback)
        if GROQ_AVAILABLE and GroqType is not None:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key and self._validate_api_key(api_key, "groq"):
                try:
                    self.groq_client = GroqType(api_key=api_key)
                    self.use_groq = True
                    status = "Fallback" if self.use_openai else "Primary"
                    logger.info(f"⚡ GROQ Llama3 client initialized (High-Speed {status})")
                except Exception as e:
                    logger.warning(f"⚠️ GROQ initialization failed: {e}")
                    self.use_groq = False
    
    def _validate_api_key(self, api_key: str, provider: str) -> bool:
        """Validate API key format and basic structure"""
        if provider == "openai":
            return api_key.startswith("sk-") and len(api_key) > 20
        elif provider == "groq":
            return api_key.startswith("gsk_") and len(api_key) > 20
        return False
    
    def _init_rate_limiter(self) -> Dict[str, List[float]]:
        """Initialize sophisticated rate limiting"""
        return {
            "openai": [],
            "groq": [],
            "template": []
        }
    
    def _get_provider_status(self) -> str:
        """Get current provider configuration status"""
        providers = []
        if self.use_openai:
            providers.append("OpenAI-GPT4")
        if self.use_groq:
            providers.append("GROQ-Llama3")
        providers.append("Template-Fallback")
        return " → ".join(providers)
    
    def _get_cache_key(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem], prompt_type: str) -> str:
        """Generate sophisticated cache key for AI responses"""
        content = json.dumps({
            "analysis": analysis_results,
            "checklist": [{
                "rule_id": item.rule_id,
                "required_ok": item.required_ok,
                "problems": item.problems
            } for item in checklist],
            "type": prompt_type
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _check_rate_limit(self, provider: str, max_per_minute: int = 60) -> bool:
        """Advanced rate limiting with sliding window"""
        now = time.time()
        requests = self.rate_limiter[provider]
        
        # Clean old requests (older than 1 minute)
        self.rate_limiter[provider] = [req_time for req_time in requests if now - req_time < 60]
        
        if len(self.rate_limiter[provider]) >= max_per_minute:
            logger.warning(f"🚫 Rate limit exceeded for {provider}")
            return False
        
        self.rate_limiter[provider].append(now)
        return True
    
    async def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check intelligent cache with TTL and provider tracking"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired:
                self.metrics.cache_hits += 1
                logger.info(f"💾 Cache hit for {cache_key[:8]}... (provider: {entry.provider})")
                return entry.content
            else:
                # Clean expired entry
                del self.cache[cache_key]
        
        self.metrics.cache_misses += 1
        return None
    
    def _update_cache(self, cache_key: str, content: str, provider: str) -> None:
        """Update cache with new content and metadata"""
        self.cache[cache_key] = CacheEntry(
            content=content,
            timestamp=datetime.now(),
            provider=provider
        )
        
        # Prevent cache from growing too large
        if len(self.cache) > 1000:
            # Remove oldest entries
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1].timestamp)
            for key, _ in sorted_entries[:100]:
                del self.cache[key]
    
    async def generate_negotiation_brief(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> Tuple[str, Dict[str, Any]]:
        """
        🎯 Generate premium negotiation prep brief with AI + advanced features
        Returns: (content, metadata)
        """
        start_time = time.time()
        cache_key = self._get_cache_key(analysis_results, checklist, "brief")
        
        # Check intelligent cache first
        cached_content = await self._check_cache(cache_key)
        if cached_content:
            return cached_content, {
                "provider": "cache",
                "response_time": 0.001,
                "cache_hit": True
            }
        
        # AI Generation Pipeline with sophisticated fallback
        content, metadata = await self._execute_ai_pipeline(
            analysis_results, checklist, "brief", cache_key
        )
        
        # Update performance metrics
        response_time = time.time() - start_time
        self.metrics.total_response_time += response_time
        metadata.update({
            "response_time": response_time,
            "cache_hit": False,
            "quality_score": self._calculate_quality_score(content)
        })
        
        logger.info(f"📋 Brief generated: {metadata['provider']} ({response_time:.2f}s, quality: {metadata['quality_score']:.1f}/10)")
        return content, metadata
    
    async def _execute_ai_pipeline(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem], 
                                  content_type: str, cache_key: str) -> Tuple[str, Dict[str, Any]]:
        """🚀 Execute sophisticated AI generation pipeline with multiple providers"""
        
        # Strategy 1: OpenAI GPT-4 (Premium Quality)
        if self.use_openai and self._check_rate_limit("openai", 50):
            try:
                if content_type == "brief":
                    content = await self._generate_brief_with_openai(analysis_results, checklist)
                else:
                    content = await self._generate_email_with_openai(analysis_results, checklist)
                
                self.metrics.openai_requests += 1
                self.metrics.openai_successes += 1
                self._update_cache(cache_key, content, "openai-gpt4")
                
                return content, {"provider": "openai-gpt4", "quality_tier": "premium"}
                
            except Exception as e:
                self.metrics.openai_failures += 1
                logger.warning(f"🔴 OpenAI failed: {e}, escalating to GROQ...")
        
        # Strategy 2: GROQ Llama3 (High-Speed Fallback)
        if self.use_groq and self._check_rate_limit("groq", 100):
            try:
                if content_type == "brief":
                    content = await self._generate_brief_with_groq(analysis_results, checklist)
                else:
                    content = await self._generate_email_with_groq(analysis_results, checklist)
                
                self.metrics.groq_requests += 1
                self.metrics.groq_successes += 1
                self._update_cache(cache_key, content, "groq-llama3")
                
                return content, {"provider": "groq-llama3", "quality_tier": "high-speed"}
                
            except Exception as e:
                self.metrics.groq_failures += 1
                logger.warning(f"🟡 GROQ failed: {e}, using expert template...")
        
        # Strategy 3: Expert Template (100% Reliable)
        self.metrics.template_fallbacks += 1
        if content_type == "brief":
            content = self._generate_brief_with_template(analysis_results, checklist)
        else:
            content = self._generate_email_with_template(analysis_results, checklist)
            
        return content, {"provider": "expert-template", "quality_tier": "reliable"}
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate content quality score based on multiple factors"""
        score = 5.0  # Base score
        
        # Length appropriateness
        if 200 <= len(content) <= 1000:
            score += 1.0
        
        # Professional keywords
        professional_terms = ["assessment", "compliance", "requirements", "analysis", "recommendation"]
        score += sum(0.2 for term in professional_terms if term.lower() in content.lower())
        
        # GSA rule citations
        if "Rule R" in content or "GSA" in content:
            score += 1.0
        
        # Structure indicators
        if "**" in content or "•" in content:  # Formatting
            score += 0.5
        
        return min(score, 10.0)
    
    async def generate_client_email(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> Tuple[str, Dict[str, Any]]:
        """
        📧 Generate professional client email with AI + advanced features
        Returns: (content, metadata)
        """
        start_time = time.time()
        cache_key = self._get_cache_key(analysis_results, checklist, "email")
        
        # Check intelligent cache first
        cached_content = await self._check_cache(cache_key)
        if cached_content:
            return cached_content, {
                "provider": "cache",
                "response_time": 0.001,
                "cache_hit": True
            }
        
        # AI Generation Pipeline
        content, metadata = await self._execute_ai_pipeline(
            analysis_results, checklist, "email", cache_key
        )
        
        # Update performance metrics
        response_time = time.time() - start_time
        self.metrics.total_response_time += response_time
        metadata.update({
            "response_time": response_time,
            "cache_hit": False,
            "quality_score": self._calculate_quality_score(content)
        })
        
        logger.info(f"📧 Email generated: {metadata['provider']} ({response_time:.2f}s, quality: {metadata['quality_score']:.1f}/10)")
        return content, metadata
    
    async def _generate_brief_with_openai(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Generate brief using OpenAI API"""
        
        # Prepare context
        context = self._prepare_context_for_ai(analysis_results, checklist)
        
        prompt = f"""You are a GSA contracting specialist preparing a negotiation brief. 

Based on the following analysis:
{context}

Generate a comprehensive negotiation prep brief (2-3 paragraphs) that:
1. Summarizes the vendor's strengths and weaknesses
2. Identifies key negotiation points and leverage areas
3. Provides specific recommendations for pricing discussions
4. Cites relevant GSA rules (R1-R5) where applicable

Be professional, concise, and focus on actionable insights."""

        try:
            if self.openai_client is None:
                raise Exception("OpenAI client not initialized")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a GSA contracting specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    async def _generate_email_with_openai(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Generate client email using OpenAI API"""
        
        context = self._prepare_context_for_ai(analysis_results, checklist)
        
        prompt = f"""You are a GSA contracting officer writing to a vendor about their submission.

Based on the following analysis:
{context}

Generate a professional, polite client email that:
1. Thanks them for their submission
2. Lists specific missing items or issues found
3. Provides clear next steps and deadlines
4. Maintains a collaborative tone

Keep it concise and actionable."""

        try:
            if self.openai_client is None:
                raise Exception("OpenAI client not initialized")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional GSA contracting officer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    async def _generate_brief_with_groq(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Generate brief using GROQ API"""
        
        # Prepare context
        context = self._prepare_context_for_ai(analysis_results, checklist)
        
        prompt = f"""You are a GSA contracting specialist preparing a negotiation brief. 

Based on the following analysis:
{context}

Generate a comprehensive negotiation prep brief (2-3 paragraphs) that:
1. Summarizes the vendor's strengths and weaknesses
2. Identifies key negotiation points and leverage areas
3. Provides specific recommendations for pricing discussions
4. Cites relevant GSA rules (R1-R5) where applicable

Be professional, concise, and focus on actionable insights."""

        try:
            if self.groq_client is None:
                raise Exception("GROQ client not initialized")
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a GSA contracting specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"GROQ API call failed: {e}")
    
    async def _generate_email_with_groq(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Generate client email using GROQ API"""
        
        context = self._prepare_context_for_ai(analysis_results, checklist)
        
        prompt = f"""You are a GSA contracting officer writing to a vendor about their submission.

Based on the following analysis:
{context}

Generate a professional, polite client email that:
1. Thanks them for their submission
2. Lists specific missing items or issues found
3. Provides clear next steps and deadlines
4. Maintains a collaborative tone

Keep it concise and actionable."""

        try:
            if self.groq_client is None:
                raise Exception("GROQ client not initialized")
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional GSA contracting officer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"GROQ API call failed: {e}")
    
    def _generate_brief_with_template(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Generate brief using template-based approach"""
        
        # Analyze strengths and weaknesses
        strengths = []
        weaknesses = []
        negotiation_points = []
        
        company_name = analysis_results.get("company_profile", {}).get("company_name", "The vendor")
        
        for item in checklist:
            if item.required_ok:
                strengths.append(f"✓ {item.description} (Rule {item.rule_id})")
            else:
                weaknesses.append(f"✗ {item.description} - {', '.join(item.problems)} (Rule {item.rule_id})")
                
                # Add specific negotiation points
                if "pricing_incomplete" in item.problems:
                    negotiation_points.append("Request detailed pricing breakdown with clear rate basis and units")
                if "past_performance_min_value_not_met" in item.problems:
                    negotiation_points.append("Require additional past performance examples or accept higher risk")
                if any("missing" in problem for problem in item.problems):
                    negotiation_points.append("Obtain missing documentation before contract award")
        
        # Generate brief
        brief_parts = []
        
        # Paragraph 1: Overall assessment
        if strengths and weaknesses:
            brief_parts.append(
                f"**Overall Assessment**: {company_name} presents a mixed profile with both compliant and deficient areas. "
                f"While they meet {len([s for s in strengths])} key requirements, there are {len(weaknesses)} areas "
                f"requiring attention before contract award."
            )
        elif strengths:
            brief_parts.append(
                f"**Overall Assessment**: {company_name} demonstrates strong compliance across all reviewed areas, "
                f"meeting {len(strengths)} key GSA requirements. This positions them as a low-risk vendor."
            )
        else:
            brief_parts.append(
                f"**Overall Assessment**: {company_name} has significant compliance gaps that must be addressed. "
                f"High risk profile requiring substantial remediation before contract consideration."
            )
        
        # Paragraph 2: Specific findings
        findings_text = "**Key Findings**: "
        if strengths:
            findings_text += f"Strengths include: {'; '.join(strengths[:3])}. "
        if weaknesses:
            findings_text += f"Critical gaps: {'; '.join(weaknesses[:3])}. "
        
        brief_parts.append(findings_text)
        
        # Paragraph 3: Negotiation strategy
        if negotiation_points:
            strategy_text = f"**Negotiation Strategy**: {' '.join(negotiation_points[:3])}. "
            if "pricing" in str(weaknesses).lower():
                strategy_text += "Focus negotiations on pricing transparency and competitive rates. "
            if "performance" in str(weaknesses).lower():
                strategy_text += "Consider requiring performance guarantees or additional references. "
        else:
            strategy_text = "**Negotiation Strategy**: Vendor meets all requirements. Focus on competitive pricing and favorable terms."
        
        brief_parts.append(strategy_text)
        
        return "\n\n".join(brief_parts)
    
    def _generate_email_with_template(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Generate client email using template-based approach"""
        
        company_name = analysis_results.get("company_profile", {}).get("company_name", "your organization")
        missing_items = []
        
        for item in checklist:
            if not item.required_ok:
                for problem in item.problems:
                    if "missing" in problem:
                        missing_items.append(f"• {problem.replace('_', ' ').title()} (per GSA Rule {item.rule_id})")
                    elif "incomplete" in problem:
                        missing_items.append(f"• Complete {problem.replace('_incomplete', '').replace('_', ' ').title()} information (per GSA Rule {item.rule_id})")
                    elif "not_met" in problem:
                        missing_items.append(f"• Address {problem.replace('_not_met', '').replace('_', ' ').title()} requirements (per GSA Rule {item.rule_id})")
        
        if missing_items:
            email_body = f"""Subject: GSA Submission Review - Additional Information Required

Dear {company_name} Team,

Thank you for your recent GSA submission. Our review team has completed the initial analysis of your documentation.

To proceed with your application, we need the following items to be addressed:

{chr(10).join(missing_items)}

Please provide the missing information within 10 business days. Once we receive these items, we will complete our review and provide next steps.

We appreciate your interest in working with GSA and look forward to your response.

Best regards,
GSA Contracting Team"""
        else:
            email_body = f"""Subject: GSA Submission Review - Complete

Dear {company_name} Team,

Thank you for your GSA submission. Our review team has completed the analysis of your documentation.

We are pleased to inform you that your submission meets all initial requirements. We will proceed with the next phase of the evaluation process and will contact you within 5 business days with further instructions.

Thank you for your thoroughness in preparing your submission.

Best regards,
GSA Contracting Team"""
        
        return email_body
    
    def _prepare_context_for_ai(self, analysis_results: Dict[str, Any], checklist: List[ChecklistItem]) -> str:
        """Prepare context for AI prompt"""
        context_parts = []
        
        # Company profile
        profile = analysis_results.get("company_profile", {})
        if profile:
            context_parts.append(f"Company: {profile.get('company_name', 'Unknown')}")
            if profile.get("uei"):
                context_parts.append(f"UEI: {profile.get('uei')}")
            if profile.get("naics"):
                context_parts.append(f"NAICS: {', '.join(map(str, profile.get('naics', [])))}")
        
        # Checklist summary
        compliant_items = [item for item in checklist if item.required_ok]
        non_compliant_items = [item for item in checklist if not item.required_ok]
        
        context_parts.append(f"Compliant Requirements: {len(compliant_items)}")
        context_parts.append(f"Non-Compliant Requirements: {len(non_compliant_items)}")
        
        if non_compliant_items:
            problems = []
            for item in non_compliant_items:
                problems.extend([f"{problem} (Rule {item.rule_id})" for problem in item.problems])
            context_parts.append(f"Issues Found: {', '.join(problems)}")
        
        return "; ".join(context_parts)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """📊 Get comprehensive performance metrics for monitoring"""
        return {
            "providers": {
                "openai": {
                    "available": self.use_openai,
                    "requests": self.metrics.openai_requests,
                    "successes": self.metrics.openai_successes,
                    "failures": self.metrics.openai_failures,
                    "success_rate": self.metrics.openai_successes / max(self.metrics.openai_requests, 1)
                },
                "groq": {
                    "available": self.use_groq,
                    "requests": self.metrics.groq_requests,
                    "successes": self.metrics.groq_successes,
                    "failures": self.metrics.groq_failures,
                    "success_rate": self.metrics.groq_successes / max(self.metrics.groq_requests, 1)
                }
            },
            "performance": {
                "average_response_time": self.metrics.average_response_time,
                "total_requests": self.metrics.openai_requests + self.metrics.groq_requests,
                "template_fallbacks": self.metrics.template_fallbacks,
                "overall_success_rate": self.metrics.success_rate
            },
            "caching": {
                "cache_size": len(self.cache),
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "cache_hit_rate": self.metrics.cache_hits / max(self.metrics.cache_hits + self.metrics.cache_misses, 1)
            },
            "system_health": self._get_system_health_score()
        }
    
    def _get_system_health_score(self) -> Dict[str, Any]:
        """🏥 Calculate system health score"""
        health_score = 10.0
        issues = []
        
        # Provider availability
        if not self.use_openai and not self.use_groq:
            health_score -= 5.0
            issues.append("No AI providers available")
        elif not self.use_openai:
            health_score -= 2.0
            issues.append("Primary AI provider (OpenAI) unavailable")
        
        # Success rate
        if self.metrics.success_rate < 0.9:
            health_score -= 2.0
            issues.append(f"Low success rate: {self.metrics.success_rate:.1%}")
        
        # Response time
        if self.metrics.average_response_time > 10.0:
            health_score -= 1.0
            issues.append(f"High average response time: {self.metrics.average_response_time:.1f}s")
        
        return {
            "score": max(health_score, 0.0),
            "status": "healthy" if health_score >= 8.0 else "warning" if health_score >= 5.0 else "critical",
            "issues": issues
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """🔍 Comprehensive health check for monitoring systems"""
        start_time = time.time()
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "providers": {},
            "cache_status": "active" if len(self.cache) > 0 else "empty",
            "uptime_check": True
        }
        
        # Test OpenAI if available
        if self.use_openai:
            try:
                # Quick test call
                if self.async_openai_client is None:
                    raise Exception("Async OpenAI client not initialized")
                
                test_response = await asyncio.wait_for(
                    self.async_openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Health check"}],
                        max_tokens=5
                    ),
                    timeout=5.0
                )
                health_data["providers"]["openai"] = {"status": "healthy", "latency": time.time() - start_time}
            except Exception as e:
                health_data["providers"]["openai"] = {"status": "unhealthy", "error": str(e)}
        
        # Test GROQ if available
        if self.use_groq:
            try:
                if self.groq_client is None:
                    raise Exception("GROQ client not initialized")
                
                test_response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.groq_client.chat.completions.create,
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": "Health check"}],
                        max_tokens=5
                    ),
                    timeout=5.0
                )
                health_data["providers"]["groq"] = {"status": "healthy", "latency": time.time() - start_time}
            except Exception as e:
                health_data["providers"]["groq"] = {"status": "unhealthy", "error": str(e)}
        
        return health_data

# Create alias for backward compatibility
AIService = EnterpriseAIService