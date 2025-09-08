"""Demo script to showcase enhanced value objects functionality."""

from datetime import date, datetime

from domain.common.enhanced_i18n import I18n
from domain.common.enhanced_enums import Gender, PetType, UserType
from domain.common.value_objects import I18nEnum
from domain.pets.pet_age import PetAge
from domain.pets.genetic_profile import GeneticProfile, GeneExpression
from domain.pets.ownership_history import OwnershipHistory, OwnershipRecord
from domain.pets.value_objects import ZygosityEnum


def demo_enhanced_i18n():
    """Demonstrate enhanced I18n value object."""
    print("=== Enhanced I18n Value Object Demo ===")
    
    # Create bilingual I18n
    i18n = I18n.create_bilingual("金毛寻回犬", "Golden Retriever")
    print(f"Bilingual I18n: {i18n}")
    print(f"Chinese text: {i18n.get_text('zh_CN')}")
    print(f"English text: {i18n.get_text('en_US')}")
    print(f"Available languages: {i18n.get_available_languages()}")
    
    # Add new language
    i18n_with_french = i18n.with_text("fr_FR", "Golden Retriever")
    print(f"With French: {i18n_with_french.get_text('fr_FR')}")
    
    # Check completeness
    print(f"Is complete (zh_CN, en_US): {i18n.is_complete([I18nEnum.ZH_CN, I18nEnum.EN_US])}")
    print()


def demo_enhanced_enums():
    """Demonstrate enhanced enum value objects."""
    print("=== Enhanced Enum Value Objects Demo ===")
    
    # Gender enum
    male_gender = Gender.male()
    print(f"Male gender: {male_gender}")
    print(f"Is male: {male_gender.is_male()}")
    print(f"Is female: {male_gender.is_female()}")
    
    # Pet type enum
    dog_type = PetType.dog()
    print(f"Dog type: {dog_type}")
    print(f"Is dog: {dog_type.is_dog()}")
    
    # User type enum
    admin_user = UserType(value="admin")
    print(f"Admin user: {admin_user}")
    print(f"Has admin privileges: {admin_user.has_admin_privileges()}")
    print(f"Can modify pets: {admin_user.can_modify_pets()}")
    print()


def demo_pet_age():
    """Demonstrate PetAge value object."""
    print("=== PetAge Value Object Demo ===")
    
    # Create pet age from birth date
    birth_date = date(2020, 5, 15)
    pet_age = PetAge.from_birth_date(birth_date)
    
    print(f"Birth date: {birth_date}")
    print(f"Age in days: {pet_age.get_age_in_days()}")
    print(f"Age in years: {pet_age.get_age_in_years()}")
    print(f"Age in years and months: {pet_age.get_age_in_years_and_months()}")
    print(f"Formatted age: {pet_age.get_formatted_age()}")
    print(f"Life stage: {pet_age.get_life_stage()}")
    print(f"Is adult: {pet_age.is_adult()}")
    print(f"Is senior: {pet_age.is_senior()}")
    print(f"Next birthday: {pet_age.get_next_birthday()}")
    print(f"Days until birthday: {pet_age.days_until_birthday()}")
    print()


def demo_genetic_profile():
    """Demonstrate GeneticProfile value object."""
    print("=== GeneticProfile Value Object Demo ===")
    
    # Create gene expressions
    gene1 = GeneExpression(
        gene_id="gene_001",
        gene_name="Color Gene",
        zygosity=ZygosityEnum.HOMOZYGOUS,
        expression_level=0.8
    )
    
    gene2 = GeneExpression(
        gene_id="gene_002",
        gene_name="Pattern Gene",
        zygosity=ZygosityEnum.HETEROZYGOUS,
        expression_level=0.6
    )
    
    # Create genetic profile
    profile = GeneticProfile.from_gene_list([gene1, gene2], "Test Profile")
    print(f"Genetic profile: {profile}")
    print(f"Profile summary: {profile.get_expression_summary()}")
    
    # Get specific gene types
    print(f"Dominant genes: {len(profile.get_dominant_genes())}")
    print(f"Heterozygous genes: {len(profile.get_heterozygous_genes())}")
    
    # Create another profile for compatibility testing
    gene3 = GeneExpression(
        gene_id="gene_001",
        gene_name="Color Gene",
        zygosity=ZygosityEnum.HETEROZYGOUS,
        expression_level=0.7
    )
    
    profile2 = GeneticProfile.from_gene_list([gene3], "Test Profile 2")
    compatibility = profile.get_compatibility_score(profile2)
    print(f"Compatibility score: {compatibility:.2f}")
    print(f"Is compatible: {profile.is_compatible_with(profile2)}")
    
    # Get breeding predictions
    predictions = profile.get_breeding_predictions(profile2)
    print(f"Breeding predictions: {predictions}")
    print()


def demo_ownership_history():
    """Demonstrate OwnershipHistory value object."""
    print("=== OwnershipHistory Value Object Demo ===")
    
    # Create ownership history with initial owner
    history = OwnershipHistory.create_with_initial_owner(
        pet_id="pet_123",
        owner_id="user_001",
        owner_name="John Doe",
        transfer_type="adoption"
    )
    
    print(f"Initial history: {history}")
    print(f"Current owner: {history.get_current_owner_id()}")
    
    # Transfer ownership
    history = history.transfer_ownership(
        new_owner_id="user_002",
        new_owner_name="Jane Smith",
        transfer_reason="Family relocation",
        transfer_type="transfer"
    )
    
    print(f"After transfer: {history}")
    print(f"Ownership count: {history.get_ownership_count()}")
    
    # Get summary
    summary = history.get_ownership_summary()
    print(f"Ownership summary: {summary}")
    
    # Get timeline
    timeline = history.get_ownership_timeline()
    print(f"Ownership timeline: {len(timeline)} events")
    
    # Check if pet has been owned by specific user
    print(f"Has been owned by user_001: {history.has_been_owned_by('user_001')}")
    print()


def main():
    """Run all value object demos."""
    print("Enhanced Value Objects Demonstration")
    print("=" * 50)
    
    try:
        demo_enhanced_i18n()
        demo_enhanced_enums()
        demo_pet_age()
        demo_genetic_profile()
        demo_ownership_history()
        
        print("All demos completed successfully!")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
