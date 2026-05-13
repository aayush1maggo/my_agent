"""Example: Google Slides Integration

This example demonstrates creating an SEO presentation using Google Slides tools.
"""
from seo_agent.tools.google_slides_tools import (
    create_presentation,
    add_slide,
    add_title_to_slide,
    add_bullet_points_to_slide,
    add_table_to_slide,
    update_table_cell,
    get_presentation
)


def create_seo_audit_presentation():
    """Create a sample SEO audit presentation"""

    # 1. Create new presentation
    print("Creating presentation...")
    result = create_presentation("SEO Audit Report - Example.com")

    if result['status'] != 'success':
        print(f"Error creating presentation: {result['error']}")
        return

    presentation_id = result['presentation_id']
    print(f"✓ Created presentation: {result['url']}")

    # 2. Get presentation details (includes first slide)
    pres_details = get_presentation(presentation_id)
    first_slide_id = pres_details['slides'][0]['object_id']

    # 3. Add title to first slide
    print("\nAdding title slide...")
    add_title_to_slide(
        presentation_id,
        first_slide_id,
        "SEO Audit Report",
        "Example.com - Q1 2025"
    )
    print("✓ Title slide created")

    # 4. Add executive summary slide
    print("\nAdding executive summary...")
    summary_slide = add_slide(presentation_id, layout='TITLE_AND_BODY')
    summary_slide_id = summary_slide['slide_id']

    add_title_to_slide(presentation_id, summary_slide_id, "Executive Summary")
    add_bullet_points_to_slide(
        presentation_id,
        summary_slide_id,
        [
            "Organic traffic increased 34% QoQ",
            "Fixed 127 technical SEO issues",
            "Improved Core Web Vitals scores by 45%",
            "Added 15 new high-quality backlinks",
            "Keyword rankings improved for 23 target terms"
        ],
        x=100,
        y=150,
        width=600,
        height=300
    )
    print("✓ Executive summary added")

    # 5. Add metrics table slide
    print("\nAdding metrics table...")
    metrics_slide = add_slide(presentation_id, layout='TITLE_ONLY')
    metrics_slide_id = metrics_slide['slide_id']

    add_title_to_slide(presentation_id, metrics_slide_id, "Key Performance Metrics")

    # Create table
    table_result = add_table_to_slide(
        presentation_id,
        metrics_slide_id,
        rows=4,
        columns=3,
        x=100,
        y=150,
        width=600,
        height=250
    )
    table_id = table_result['table_id']

    # Populate table headers
    update_table_cell(presentation_id, table_id, 0, 0, "Metric")
    update_table_cell(presentation_id, table_id, 0, 1, "Current")
    update_table_cell(presentation_id, table_id, 0, 2, "Change")

    # Populate table data
    update_table_cell(presentation_id, table_id, 1, 0, "Organic Sessions")
    update_table_cell(presentation_id, table_id, 1, 1, "12,543")
    update_table_cell(presentation_id, table_id, 1, 2, "+34%")

    update_table_cell(presentation_id, table_id, 2, 0, "Avg. Position")
    update_table_cell(presentation_id, table_id, 2, 1, "8.2")
    update_table_cell(presentation_id, table_id, 2, 2, "+2.3")

    update_table_cell(presentation_id, table_id, 3, 0, "Total Backlinks")
    update_table_cell(presentation_id, table_id, 3, 1, "487")
    update_table_cell(presentation_id, table_id, 3, 2, "+15")

    print("✓ Metrics table added")

    # 6. Add recommendations slide
    print("\nAdding recommendations...")
    recs_slide = add_slide(presentation_id, layout='TITLE_AND_BODY')
    recs_slide_id = recs_slide['slide_id']

    add_title_to_slide(presentation_id, recs_slide_id, "Next Steps")
    add_bullet_points_to_slide(
        presentation_id,
        recs_slide_id,
        [
            "Optimize remaining product pages for target keywords",
            "Build backlinks from industry publications",
            "Implement schema markup for local SEO",
            "Create content targeting featured snippet opportunities"
        ],
        x=100,
        y=150,
        width=600,
        height=280
    )
    print("✓ Recommendations added")

    print(f"\n{'='*60}")
    print(f"✓ Presentation created successfully!")
    print(f"📊 View at: {result['url']}")
    print(f"{'='*60}")

    return presentation_id


if __name__ == "__main__":
    create_seo_audit_presentation()
