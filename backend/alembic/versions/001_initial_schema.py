"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-07-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('email'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_organizations_id', 'organizations', ['id'])

    # Create programs table
    op.create_table('programs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_programs_id', 'programs', ['id'])

    # Create questionnaires table
    op.create_table('questionnaires',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_questionnaires_id', 'questionnaires', ['id'])

    # Create questions table
    op.create_table('questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('questionnaire_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['questionnaire_id'], ['questionnaires.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_questions_id', 'questions', ['id'])

    # Create calibration_answers table
    op.create_table('calibration_answers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('question_key', sa.String(length=255), nullable=False),
        sa.Column('answer_value', sa.JSON(), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calibration_answers_id', 'calibration_answers', ['id'])

    # Create ai_guidelines table
    op.create_table('ai_guidelines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('section', sa.String(length=255), nullable=False),
        sa.Column('weight', sa.Integer(), nullable=False, default=1),
        sa.Column('criteria', sa.JSON(), nullable=False),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_guidelines_id', 'ai_guidelines', ['id'])

    # Create applications table
    op.create_table('applications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('unique_id', sa.String(length=255), nullable=False),
        sa.Column('startup_name', sa.String(length=255), nullable=False),
        sa.Column('contact_email', sa.String(length=255), nullable=False),
        sa.Column('is_submitted', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('processing_status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('questionnaire_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.ForeignKeyConstraint(['questionnaire_id'], ['questionnaires.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unique_id')
    )
    op.create_index('ix_applications_id', 'applications', ['id'])
    op.create_index('ix_applications_unique_id', 'applications', ['unique_id'])

    # Create responses table
    op.create_table('responses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('response_value', sa.JSON(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_responses_id', 'responses', ['id'])

    # Create uploaded_files table
    op.create_table('uploaded_files',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extraction_status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_uploaded_files_id', 'uploaded_files', ['id'])

    # Create reports table
    op.create_table('reports',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('overall_summary', sa.Text(), nullable=False),
        sa.Column('problem_solution_score', sa.Float(), nullable=False),
        sa.Column('problem_solution_content', sa.Text(), nullable=False),
        sa.Column('customer_profile_score', sa.Float(), nullable=False),
        sa.Column('customer_profile_content', sa.Text(), nullable=False),
        sa.Column('product_technology_score', sa.Float(), nullable=False),
        sa.Column('product_technology_content', sa.Text(), nullable=False),
        sa.Column('team_structure_score', sa.Float(), nullable=False),
        sa.Column('team_structure_content', sa.Text(), nullable=False),
        sa.Column('market_opportunity_score', sa.Float(), nullable=False),
        sa.Column('market_opportunity_content', sa.Text(), nullable=False),
        sa.Column('financial_overview_score', sa.Float(), nullable=False),
        sa.Column('financial_overview_content', sa.Text(), nullable=False),
        sa.Column('key_challenges_score', sa.Float(), nullable=False),
        sa.Column('key_challenges_content', sa.Text(), nullable=False),
        sa.Column('validation_achievements_score', sa.Float(), nullable=False),
        sa.Column('validation_achievements_content', sa.Text(), nullable=False),
        sa.Column('investigation_areas_score', sa.Float(), nullable=False),
        sa.Column('investigation_areas_content', sa.Text(), nullable=False),
        sa.Column('pdf_file_path', sa.String(length=500), nullable=True),
        sa.Column('pdf_generated_at', sa.DateTime(), nullable=True),
        sa.Column('generation_status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('is_latest', sa.Boolean(), nullable=False, default=True),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reports_id', 'reports', ['id'])

    # Create scores table
    op.create_table('scores',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('category', sa.String(length=255), nullable=False),
        sa.Column('score_value', sa.Float(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('is_overridden', sa.Boolean(), nullable=False, default=False),
        sa.Column('original_score', sa.Float(), nullable=True),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scores_id', 'scores', ['id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('scores')
    op.drop_table('reports')
    op.drop_table('uploaded_files')
    op.drop_table('responses')
    op.drop_table('applications')
    op.drop_table('ai_guidelines')
    op.drop_table('calibration_answers')
    op.drop_table('questions')
    op.drop_table('questionnaires')
    op.drop_table('programs')
    op.drop_table('organizations')