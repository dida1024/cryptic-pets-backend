"""Genetic profile value object for handling gene combinations."""

from typing import Any

from pydantic import Field, field_validator

from domain.common.value_object_base import ValueObject
from domain.pets.value_objects import ZygosityEnum


class GeneExpression(ValueObject):
    """Individual gene expression value object."""

    gene_id: str = Field(..., description="Gene identifier")
    gene_name: str = Field(..., description="Gene name")
    zygosity: ZygosityEnum = Field(..., description="Gene zygosity")
    expression_level: float = Field(ge=0.0, le=1.0, description="Expression level (0.0 to 1.0)")

    @field_validator('gene_id', 'gene_name')
    @classmethod
    def validate_string_fields(cls, v: str) -> str:
        """Validate string fields."""
        if not v or not v.strip():
            raise ValueError("Gene ID and name cannot be empty")
        return v.strip()

    def is_dominant(self) -> bool:
        """Check if gene is expressed dominantly."""
        return self.zygosity in {ZygosityEnum.HOMOZYGOUS, ZygosityEnum.HETEROZYGOUS} and self.expression_level > 0.5

    def is_recessive(self) -> bool:
        """Check if gene is expressed recessively."""
        return self.zygosity == ZygosityEnum.HOMOZYGOUS and self.expression_level <= 0.5

    def is_heterozygous(self) -> bool:
        """Check if gene is heterozygous."""
        return self.zygosity == ZygosityEnum.HETEROZYGOUS

    def is_homozygous(self) -> bool:
        """Check if gene is homozygous."""
        return self.zygosity == ZygosityEnum.HOMOZYGOUS

    def get_expression_strength(self) -> str:
        """Get expression strength description."""
        if self.expression_level >= 0.8:
            return "strong"
        elif self.expression_level >= 0.5:
            return "moderate"
        elif self.expression_level >= 0.2:
            return "weak"
        else:
            return "minimal"


class GeneticProfile(ValueObject):
    """Genetic profile value object for comprehensive gene combination handling."""

    gene_expressions: dict[str, GeneExpression] = Field(
        default_factory=dict,
        description="Dictionary of gene expressions by gene ID"
    )
    profile_name: str | None = Field(None, description="Optional profile name")
    created_at: str | None = Field(None, description="Profile creation timestamp")

    @field_validator('gene_expressions')
    @classmethod
    def validate_gene_expressions(cls, v: dict[str, GeneExpression]) -> dict[str, GeneExpression]:
        """Validate gene expressions dictionary."""
        if not v:
            raise ValueError("Genetic profile must contain at least one gene expression")

        # Check for duplicate gene IDs
        gene_ids = [expr.gene_id for expr in v.values()]
        if len(gene_ids) != len(set(gene_ids)):
            raise ValueError("Duplicate gene IDs found in genetic profile")

        return v

    @field_validator('profile_name')
    @classmethod
    def validate_profile_name(cls, v: str | None) -> str | None:
        """Validate profile name."""
        if v is not None and not v.strip():
            raise ValueError("Profile name cannot be empty")
        return v.strip() if v else None

    @classmethod
    def create_empty(cls, profile_name: str | None = None) -> "GeneticProfile":
        """Create an empty genetic profile."""
        return cls(gene_expressions={}, profile_name=profile_name)

    @classmethod
    def from_gene_list(cls, gene_expressions: list[GeneExpression], profile_name: str | None = None) -> "GeneticProfile":
        """Create genetic profile from a list of gene expressions."""
        gene_dict = {expr.gene_id: expr for expr in gene_expressions}
        return cls(gene_expressions=gene_dict, profile_name=profile_name)

    def add_gene_expression(self, gene_expression: GeneExpression) -> "GeneticProfile":
        """Add a gene expression to the profile."""
        updated_expressions = dict(self.gene_expressions)
        updated_expressions[gene_expression.gene_id] = gene_expression
        return self.copy_with(gene_expressions=updated_expressions)

    def remove_gene_expression(self, gene_id: str) -> "GeneticProfile":
        """Remove a gene expression from the profile."""
        if gene_id not in self.gene_expressions:
            raise ValueError(f"Gene expression for {gene_id} not found")

        updated_expressions = dict(self.gene_expressions)
        del updated_expressions[gene_id]

        if not updated_expressions:
            raise ValueError("Cannot remove the last gene expression from profile")

        return self.copy_with(gene_expressions=updated_expressions)

    def update_gene_expression(self, gene_id: str, zygosity: ZygosityEnum, expression_level: float) -> "GeneticProfile":
        """Update a gene expression in the profile."""
        if gene_id not in self.gene_expressions:
            raise ValueError(f"Gene expression for {gene_id} not found")

        current_expr = self.gene_expressions[gene_id]
        updated_expr = current_expr.copy_with(
            zygosity=zygosity,
            expression_level=expression_level
        )

        updated_expressions = dict(self.gene_expressions)
        updated_expressions[gene_id] = updated_expr

        return self.copy_with(gene_expressions=updated_expressions)

    def get_gene_expression(self, gene_id: str) -> GeneExpression | None:
        """Get gene expression by gene ID."""
        return self.gene_expressions.get(gene_id)

    def has_gene(self, gene_id: str) -> bool:
        """Check if profile contains a specific gene."""
        return gene_id in self.gene_expressions

    def get_dominant_genes(self) -> list[GeneExpression]:
        """Get all dominantly expressed genes."""
        return [expr for expr in self.gene_expressions.values() if expr.is_dominant()]

    def get_recessive_genes(self) -> list[GeneExpression]:
        """Get all recessively expressed genes."""
        return [expr for expr in self.gene_expressions.values() if expr.is_recessive()]

    def get_heterozygous_genes(self) -> list[GeneExpression]:
        """Get all heterozygous genes."""
        return [expr for expr in self.gene_expressions.values() if expr.is_heterozygous()]

    def get_homozygous_genes(self) -> list[GeneExpression]:
        """Get all homozygous genes."""
        return [expr for expr in self.gene_expressions.values() if expr.is_homozygous()]

    def get_expression_summary(self) -> dict[str, Any]:
        """Get summary of gene expressions."""
        total_genes = len(self.gene_expressions)
        dominant_count = len(self.get_dominant_genes())
        recessive_count = len(self.get_recessive_genes())
        heterozygous_count = len(self.get_heterozygous_genes())
        homozygous_count = len(self.get_homozygous_genes())

        avg_expression = sum(expr.expression_level for expr in self.gene_expressions.values()) / total_genes if total_genes > 0 else 0.0

        return {
            "total_genes": total_genes,
            "dominant_genes": dominant_count,
            "recessive_genes": recessive_count,
            "heterozygous_genes": heterozygous_count,
            "homozygous_genes": homozygous_count,
            "average_expression_level": round(avg_expression, 3),
            "profile_name": self.profile_name
        }

    def get_compatibility_score(self, other: "GeneticProfile") -> float:
        """Calculate compatibility score with another genetic profile."""
        if not self.gene_expressions or not other.gene_expressions:
            return 0.0

        common_genes = set(self.gene_expressions.keys()) & set(other.gene_expressions.keys())
        if not common_genes:
            return 0.0

        total_score = 0.0
        for gene_id in common_genes:
            self_expr = self.gene_expressions[gene_id]
            other_expr = other.gene_expressions[gene_id]

            # Calculate similarity based on zygosity and expression level
            zygosity_match = 1.0 if self_expr.zygosity == other_expr.zygosity else 0.5
            expression_similarity = 1.0 - abs(self_expr.expression_level - other_expr.expression_level)

            gene_score = (zygosity_match + expression_similarity) / 2.0
            total_score += gene_score

        return total_score / len(common_genes)

    def is_compatible_with(self, other: "GeneticProfile", threshold: float = 0.7) -> bool:
        """Check if this profile is compatible with another profile."""
        return self.get_compatibility_score(other) >= threshold

    def get_breeding_predictions(self, other: "GeneticProfile") -> dict[str, Any]:
        """Get breeding predictions with another genetic profile."""
        if not self.gene_expressions or not other.gene_expressions:
            return {"error": "Both profiles must contain gene expressions"}

        predictions = {
            "compatibility_score": self.get_compatibility_score(other),
            "potential_offspring_traits": [],
            "genetic_diversity": 0.0,
            "risk_factors": []
        }

        # Analyze potential offspring traits
        for gene_id in set(self.gene_expressions.keys()) | set(other.gene_expressions.keys()):
            self_expr = self.gene_expressions.get(gene_id)
            other_expr = other.gene_expressions.get(gene_id)

            if self_expr and other_expr:
                # Both parents have this gene
                if self_expr.is_homozygous() and other_expr.is_homozygous():
                    predictions["potential_offspring_traits"].append({
                        "gene_id": gene_id,
                        "gene_name": self_expr.gene_name,
                        "offspring_zygosity": "homozygous",
                        "probability": 1.0
                    })
                elif self_expr.is_heterozygous() or other_expr.is_heterozygous():
                    predictions["potential_offspring_traits"].append({
                        "gene_id": gene_id,
                        "gene_name": self_expr.gene_name,
                        "offspring_zygosity": "heterozygous",
                        "probability": 0.5
                    })
            elif self_expr or other_expr:
                # Only one parent has this gene
                expr = self_expr or other_expr
                predictions["potential_offspring_traits"].append({
                    "gene_id": gene_id,
                    "gene_name": expr.gene_name,
                    "offspring_zygosity": "heterozygous",
                    "probability": 0.5
                })

        # Calculate genetic diversity
        all_genes = set(self.gene_expressions.keys()) | set(other.gene_expressions.keys())
        common_genes = set(self.gene_expressions.keys()) & set(other.gene_expressions.keys())
        predictions["genetic_diversity"] = len(common_genes) / len(all_genes) if all_genes else 0.0

        return predictions

    def __len__(self) -> int:
        """Return the number of gene expressions."""
        return len(self.gene_expressions)

    def __contains__(self, gene_id: str) -> bool:
        """Check if gene ID is in the profile."""
        return gene_id in self.gene_expressions

    def __str__(self) -> str:
        """String representation of the genetic profile."""
        name = self.profile_name or "Unnamed Profile"
        gene_count = len(self.gene_expressions)
        return f"{name} ({gene_count} genes)"
