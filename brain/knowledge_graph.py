"""
Jephthah Knowledge Graph
Self-learning entity and relationship storage for content generation

This allows Jephthah to:
- Store concepts and their relationships
- Build a growing knowledge base
- Generate content from connected knowledge
- Learn from what he reads
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict
import re

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from loguru import logger

from config.settings import DATA_DIR

Base = declarative_base()


class Entity(Base):
    """A concept, topic, or fact in the knowledge graph"""
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True)
    entity_type = Column(String(50), index=True)  # concept, topic, person, company, technology
    description = Column(Text)
    properties = Column(JSON, default={})  # Additional attributes
    importance = Column(Float, default=0.5)  # 0-1 how important this entity is
    access_count = Column(Integer, default=0)  # How often accessed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Relationship(Base):
    """Connection between two entities"""
    __tablename__ = "entity_relationships"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("entities.id"), index=True)
    target_id = Column(Integer, ForeignKey("entities.id"), index=True)
    relationship_type = Column(String(100))  # is_a, part_of, related_to, used_for, etc.
    strength = Column(Float, default=0.5)  # 0-1 how strong the relationship is
    context = Column(Text)  # Context where this relationship was learned
    created_at = Column(DateTime, default=datetime.utcnow)


class Fact(Base):
    """A learned fact or piece of information"""
    __tablename__ = "facts"
    
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("entities.id"), index=True)
    predicate = Column(String(255))  # What is being said about the subject
    object_value = Column(Text)  # The value/answer
    confidence = Column(Float, default=0.8)  # How confident in this fact
    source = Column(String(500))  # Where this was learned
    verified = Column(Integer, default=0)  # Number of times verified
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeGraph:
    """
    Neural-like knowledge storage that grows and improves over time.
    Allows content generation from pure memory without API calls.
    """
    
    def __init__(self):
        db_path = DATA_DIR / "knowledge_graph.db"
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # In-memory cache for fast access
        self._entity_cache: Dict[str, int] = {}
        self._load_cache()
        
        logger.info(f"Knowledge Graph initialized at {db_path}")
    
    def _load_cache(self):
        """Load entity names to cache for fast lookup"""
        session = self.Session()
        try:
            entities = session.query(Entity.id, Entity.name).all()
            self._entity_cache = {e.name.lower(): e.id for e in entities}
        finally:
            session.close()
    
    # === ENTITY MANAGEMENT ===
    
    def add_entity(self, name: str, entity_type: str, description: str = "",
                   properties: Dict = None, importance: float = 0.5) -> int:
        """Add a new entity to the knowledge graph"""
        name_lower = name.lower().strip()
        
        if name_lower in self._entity_cache:
            return self._entity_cache[name_lower]
        
        session = self.Session()
        try:
            entity = Entity(
                name=name,
                entity_type=entity_type,
                description=description,
                properties=properties or {},
                importance=importance
            )
            session.add(entity)
            session.commit()
            
            self._entity_cache[name_lower] = entity.id
            logger.debug(f"Added entity: {name} ({entity_type})")
            return entity.id
        finally:
            session.close()
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get entity by name"""
        session = self.Session()
        try:
            entity = session.query(Entity).filter(
                Entity.name.ilike(name)
            ).first()
            if entity:
                entity.access_count += 1
                session.commit()
            return entity
        finally:
            session.close()
    
    def get_entity_by_id(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID"""
        session = self.Session()
        try:
            return session.query(Entity).filter_by(id=entity_id).first()
        finally:
            session.close()
    
    # === RELATIONSHIP MANAGEMENT ===
    
    def add_relationship(self, source: str, target: str, rel_type: str,
                        strength: float = 0.5, context: str = "") -> bool:
        """Create a relationship between two entities"""
        source_id = self._entity_cache.get(source.lower())
        target_id = self._entity_cache.get(target.lower())
        
        if not source_id or not target_id:
            return False
        
        session = self.Session()
        try:
            # Check if relationship exists
            existing = session.query(Relationship).filter_by(
                source_id=source_id, 
                target_id=target_id,
                relationship_type=rel_type
            ).first()
            
            if existing:
                # Strengthen existing relationship
                existing.strength = min(1.0, existing.strength + 0.1)
                session.commit()
                return True
            
            rel = Relationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=rel_type,
                strength=strength,
                context=context
            )
            session.add(rel)
            session.commit()
            return True
        finally:
            session.close()
    
    def get_related_entities(self, entity_name: str, rel_type: str = None,
                            limit: int = 20) -> List[Tuple[Entity, str, float]]:
        """Get entities related to the given entity"""
        entity_id = self._entity_cache.get(entity_name.lower())
        if not entity_id:
            return []
        
        session = self.Session()
        try:
            query = session.query(Relationship).filter(
                (Relationship.source_id == entity_id) | 
                (Relationship.target_id == entity_id)
            )
            
            if rel_type:
                query = query.filter_by(relationship_type=rel_type)
            
            relationships = query.order_by(Relationship.strength.desc()).limit(limit).all()
            
            results = []
            for rel in relationships:
                other_id = rel.target_id if rel.source_id == entity_id else rel.source_id
                other_entity = session.query(Entity).filter_by(id=other_id).first()
                if other_entity:
                    results.append((other_entity, rel.relationship_type, rel.strength))
            
            return results
        finally:
            session.close()
    
    # === FACT MANAGEMENT ===
    
    def add_fact(self, subject: str, predicate: str, object_value: str,
                confidence: float = 0.8, source: str = "") -> bool:
        """Add a fact about an entity"""
        subject_id = self._entity_cache.get(subject.lower())
        if not subject_id:
            # Auto-create entity
            subject_id = self.add_entity(subject, "concept")
        
        session = self.Session()
        try:
            # Check for existing fact
            existing = session.query(Fact).filter_by(
                subject_id=subject_id,
                predicate=predicate
            ).first()
            
            if existing:
                existing.verified += 1
                existing.confidence = min(1.0, existing.confidence + 0.05)
                session.commit()
                return True
            
            fact = Fact(
                subject_id=subject_id,
                predicate=predicate,
                object_value=object_value,
                confidence=confidence,
                source=source
            )
            session.add(fact)
            session.commit()
            return True
        finally:
            session.close()
    
    def get_facts(self, subject: str) -> List[Dict]:
        """Get all facts about an entity"""
        subject_id = self._entity_cache.get(subject.lower())
        if not subject_id:
            return []
        
        session = self.Session()
        try:
            facts = session.query(Fact).filter_by(subject_id=subject_id).order_by(
                Fact.confidence.desc()
            ).all()
            
            return [
                {
                    "predicate": f.predicate,
                    "value": f.object_value,
                    "confidence": f.confidence,
                    "verified": f.verified
                }
                for f in facts
            ]
        finally:
            session.close()
    
    # === LEARNING FROM TEXT ===
    
    def learn_from_text(self, text: str, source: str = "web") -> int:
        """Extract entities, relationships, and facts from text"""
        learned_count = 0
        
        # Extract key terms (simple approach - can be enhanced)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        for word in set(words):
            if len(word) > 2:
                self.add_entity(word, "concept", source=source)
                learned_count += 1
        
        # Extract patterns like "X is Y" or "X are Y"
        is_patterns = re.findall(r'(\w+)\s+(?:is|are)\s+(?:a|an|the)?\s*(\w+)', text.lower())
        for subject, obj in is_patterns:
            if len(subject) > 2 and len(obj) > 2:
                self.add_fact(subject, "is_a", obj, source=source)
                learned_count += 1
        
        # Extract "used for" patterns
        used_for = re.findall(r'(\w+)\s+(?:is used for|used for|for)\s+(\w+)', text.lower())
        for subject, purpose in used_for:
            if len(subject) > 2 and len(purpose) > 2:
                self.add_fact(subject, "used_for", purpose, source=source)
                learned_count += 1
        
        logger.info(f"Learned {learned_count} items from text ({source})")
        return learned_count
    
    # === CONTENT RETRIEVAL ===
    
    def get_knowledge_about(self, topic: str, depth: int = 2) -> Dict:
        """Get comprehensive knowledge about a topic for content generation"""
        result = {
            "topic": topic,
            "description": "",
            "facts": [],
            "related_topics": [],
            "related_facts": []
        }
        
        entity = self.get_entity(topic)
        if entity:
            result["description"] = entity.description
        
        result["facts"] = self.get_facts(topic)
        
        # Get related entities
        related = self.get_related_entities(topic, limit=10)
        for ent, rel_type, strength in related:
            result["related_topics"].append({
                "name": ent.name,
                "type": ent.entity_type,
                "relationship": rel_type,
                "description": ent.description[:200] if ent.description else ""
            })
            
            # Get facts about related entities
            if depth > 1:
                related_facts = self.get_facts(ent.name)[:3]
                result["related_facts"].extend(related_facts)
        
        return result
    
    def get_random_knowledge(self, entity_type: str = None, limit: int = 5) -> List[Entity]:
        """Get random entities for content inspiration"""
        session = self.Session()
        try:
            from sqlalchemy.sql.expression import func
            query = session.query(Entity)
            if entity_type:
                query = query.filter_by(entity_type=entity_type)
            return query.order_by(func.random()).limit(limit).all()
        finally:
            session.close()
    
    # === STATISTICS ===
    
    def get_stats(self) -> Dict:
        """Get knowledge graph statistics"""
        session = self.Session()
        try:
            return {
                "entities": session.query(Entity).count(),
                "relationships": session.query(Relationship).count(),
                "facts": session.query(Fact).count(),
                "top_entities": [
                    e.name for e in session.query(Entity).order_by(
                        Entity.access_count.desc()
                    ).limit(10).all()
                ]
            }
        finally:
            session.close()


# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()
