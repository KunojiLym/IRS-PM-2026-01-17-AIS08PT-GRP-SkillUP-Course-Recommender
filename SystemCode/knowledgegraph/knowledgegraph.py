from neo4j import GraphDatabase
from typing import Dict, Optional
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── ENVIRONMENT DETECTION ─────────────────────────────────────────────────────
try:
    dbutils  # noqa
    IN_DATABRICKS = True
except NameError:
    IN_DATABRICKS = False
    logger.warning("⚠️ Running outside Databricks - Neo4j operations will fail without proper configuration")

# ── NEO4J CONNECTION SETUP ────────────────────────────────────────────────────
URI = None
AUTH = None
NEO4J_DATABASE = None

if IN_DATABRICKS:
    try:
        URI = dbutils.secrets.get(scope="skillup", key="NEO4J_URL")
        AUTH = (
            dbutils.secrets.get(scope="skillup", key="NEO4J_USER"),
            dbutils.secrets.get(scope="skillup", key="NEO4J_PASSWORD")
        )
        NEO4J_DATABASE = dbutils.secrets.get(scope="skillup", key="NEO4J_DATABASE")
        logger.info("✅ Neo4j credentials loaded from Databricks secrets")
        
        # Verify connectivity on module load (non-blocking)
        try:
            with GraphDatabase.driver(URI, auth=AUTH) as driver:
                driver.verify_connectivity()
                logger.info("✅ Neo4j connection verified successfully")
        except Exception as conn_err:
            logger.warning(f"⚠️ Neo4j connectivity check failed: {conn_err}")
            logger.warning("Functions will attempt to connect on-demand")
            
    except Exception as secret_err:
        logger.error(f"❌ Failed to load Neo4j secrets: {secret_err}")
        logger.error("Ensure secrets are configured in scope 'skillup' with keys: NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE")
else:
    # Local development fallback
    import os
    URI = os.getenv("NEO4J_URL")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
    
    if URI and NEO4J_USER and NEO4J_PASSWORD:
        AUTH = (NEO4J_USER, NEO4J_PASSWORD)
        logger.info("✅ Neo4j credentials loaded from environment variables")
    else:
        logger.warning("⚠️ Neo4j credentials not configured. Set environment variables: NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD")


def get_skills_from_job(job_title: str) -> Optional[Dict[str, int]]:
    """
    Extracts skills required for a given job title from the Neo4j database 
    and returns a dictionary of skill names and their frequencies.
    
    Args:
        job_title (str): The job title to search for.
        
    Returns:
        Dict[str, int]: A dictionary of skill names and their frequencies.
                        Returns None if an error occurs.
                        
    Raises:
        ValueError: If job_title contains invalid characters.
        ConnectionError: If unable to connect to Neo4j.
    """
    # Validate job_title FIRST (before credential check)
    if not job_title or not job_title.strip():
        raise ValueError("job_title cannot be empty")
        
    if not re.match(r"^[\w\s\-]+$", job_title):
        raise ValueError("Invalid job_title: only alphanumeric, spaces, and hyphens allowed.")
    
    # THEN validate credentials are available
    if not URI or not AUTH:
        error_msg = "Neo4j credentials not configured. Cannot execute query."
        logger.error(f"❌ {error_msg}")
        raise ConnectionError(error_msg)
    
    return_list = []
    
    try:
        logger.info(f"🔍 Querying Neo4j for skills related to job title: '{job_title}'")
        
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            records, summary, keys = driver.execute_query("""
                MATCH (r:Role)-[Requires]->(s:Skill)
                WHERE r.title CONTAINS $job_title
                RETURN DISTINCT s.skill_name, count(s) as skill_count
                ORDER BY skill_count DESC
                LIMIT 10
                """,
                job_title=job_title,
                database_=NEO4J_DATABASE,
            )
            
            # Process results
            for record in records:
                skill_name = record["s.skill_name"]
                skill_count = record["skill_count"]
                return_list.append({skill_name: skill_count})
                logger.debug(f"  - {skill_name}: {skill_count}")
            
            # Log summary information
            logger.info(
                f"✅ Query returned {len(records)} skills in "
                f"{summary.result_available_after}ms"
            )
            
            if not return_list:
                logger.warning(f"⚠️ No skills found for job title: '{job_title}'")
            
            return return_list
            
    except Exception as e:
        logger.error(f"❌ Error querying Neo4j for job title '{job_title}': {e}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Re-raise specific exceptions
        if "authentication" in str(e).lower():
            raise ConnectionError(f"Neo4j authentication failed: {e}") from e
        elif "connection" in str(e).lower():
            raise ConnectionError(f"Cannot connect to Neo4j at {URI}: {e}") from e
        else:
            # For other errors, log and return None instead of crashing
            logger.error("Returning None due to error")
            return None


def extract_all_role_skill_mappings():
    """
    Extracts ALL role-skill mappings from Neo4j and returns structured data
    for the knowledge graph output table.
    
    Returns:
        list: List of dictionaries with schema:
              - role (str): Job title/role name
              - skill_name (str): Required skill name
              - demand_count (int): Frequency/count of this skill for the role
              - category (str): Skill category (Technical, Soft, etc.)
              - prerequisites (list): List of prerequisite skills
    """
    if not URI or not AUTH:
        error_msg = "Neo4j credentials not configured. Cannot execute query."
        logger.error(f"❌ {error_msg}")
        raise ConnectionError(error_msg)
    
    results = []
    
    try:
        logger.info("🔍 Extracting all role-skill mappings from Neo4j...")
        
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            # Query to get all role-skill relationships with counts
            records, summary, keys = driver.execute_query("""
                MATCH (r:Role)-[req:Requires]->(s:Skill)
                RETURN r.title AS role, 
                       s.skill_name AS skill_name,
                       count(req) AS demand_count,
                       COALESCE(s.category, 'Technical') AS category
                ORDER BY r.title, demand_count DESC
                """,
                database_=NEO4J_DATABASE,
            )
            
            logger.info(f"✅ Retrieved {len(records)} role-skill mappings")
            
            # Process results
            for record in records:
                role_data = {
                    "role": record["role"],
                    "skill_name": record["skill_name"],
                    "demand_count": record["demand_count"],
                    "category": record["category"],
                    "prerequisites": []  # Will be populated separately
                }
                results.append(role_data)
            
            # Query to get skill prerequisites
            logger.info("🔍 Extracting skill prerequisites...")
            prereq_records, _, _ = driver.execute_query("""
                MATCH (s1:Skill)-[:Prerequisite]->(s2:Skill)
                RETURN s1.skill_name AS skill, 
                       collect(s2.skill_name) AS prerequisites
                """,
                database_=NEO4J_DATABASE,
            )
            
            # Build prerequisite mapping
            prereq_map = {}
            for record in prereq_records:
                prereq_map[record["skill"]] = record["prerequisites"]
            
            # Add prerequisites to results
            for item in results:
                item["prerequisites"] = prereq_map.get(item["skill_name"], [])
            
            logger.info(f"✅ Knowledge graph extraction complete: {len(results)} records")
            return results
            
    except Exception as e:
        logger.error(f"❌ Error extracting role-skill mappings: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise


def write_kg_output_to_delta(output_table="workspace.default.knowledge_graph_output"):
    """
    Extracts role-skill mappings from Neo4j and writes to Delta table.
    
    Args:
        output_table (str): Fully qualified Delta table name
    """
    if not IN_DATABRICKS:
        logger.error("❌ This function requires Databricks environment with PySpark")
        return
    
    logger.info(f"📊 Starting Knowledge Graph export to {output_table}")
    
    # Extract data from Neo4j
    kg_data = extract_all_role_skill_mappings()
    
    if not kg_data:
        logger.warning("⚠️ No data extracted from Neo4j. Nothing to write.")
        return
    
    # Convert to Spark DataFrame
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
    
    schema = StructType([
        StructField("role", StringType(), False),
        StructField("skill_name", StringType(), False),
        StructField("demand_count", IntegerType(), False),
        StructField("category", StringType(), False),
        StructField("prerequisites", ArrayType(StringType()), False)
    ])
    
    df = spark.createDataFrame(kg_data, schema=schema)
    
    logger.info(f"✅ Created DataFrame with {df.count()} rows")
    
    # Write to Delta table (overwrite mode to refresh data)
    try:
        df.write.format("delta").mode("overwrite").saveAsTable(output_table)
        logger.info(f"✅ Successfully wrote knowledge graph output to {output_table}")
        
        # Display summary
        print("\n" + "="*70)
        print("KNOWLEDGE GRAPH OUTPUT SUMMARY")
        print("="*70)
        summary_df = spark.sql(f"""
            SELECT role, 
                   COUNT(DISTINCT skill_name) as total_skills,
                   SUM(demand_count) as total_demand
            FROM {output_table}
            GROUP BY role
            ORDER BY total_demand DESC
        """)
        summary_df.show(20, truncate=False)
        
    except Exception as e:
        logger.error(f"❌ Failed to write to Delta table: {e}")
        raise


# ── MAIN EXECUTION ────────────────────────────────────────────────────────────
if __name__ == "__main__" and IN_DATABRICKS:
    logger.info("="*70)
    logger.info("KNOWLEDGE GRAPH EXTRACTION PIPELINE")
    logger.info("="*70)
    
    try:
        write_kg_output_to_delta()
        logger.info("✅ Knowledge Graph pipeline completed successfully")
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise
