"""
Tests for analysis formatting and display.

These tests verify:
- Page includes "Answer:" labels for rendered analysis
- Percentages are formatted with exactly two decimal places
"""
import pytest
import re
from bs4 import BeautifulSoup


@pytest.mark.analysis
def test_page_includes_answer_labels():
    """Test that page includes 'Answer:' labels for rendered analysis."""
    from app import create_app
    
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Test Q2', 'query': 'SELECT 2', 'answer': '50.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Test Q5', 'query': 'SELECT 5', 'answer': '75.50%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Test Q10', 'query': 'SELECT 10', 'answer': '60.25%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    
    # Check that "Answer:" label exists in the HTML
    assert 'Answer:' in html, "Page must include 'Answer:' labels"
    
    # Use BeautifulSoup to find answer label elements
    soup = BeautifulSoup(html, 'html.parser')
    answer_labels = soup.find_all(class_='answer-label-prefix')
    assert len(answer_labels) >= 1, "Should have at least one Answer: label"


@pytest.mark.analysis
def test_percentages_formatted_with_two_decimals():
    """Test that any percentage is formatted with exactly two decimal places."""
    from app import create_app
    
    # Include various percentage formats in mock data
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'Percentage test 1', 'query': 'SELECT 2', 'answer': '39.28%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Percentage test 2', 'query': 'SELECT 5', 'answer': '100.00%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Percentage test 3', 'query': 'SELECT 10', 'answer': '0.56%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    
    # Find all percentages in the HTML using regex
    # Pattern: digits, optional decimal point, digits, followed by %
    percentage_pattern = r'\d+\.\d+%'
    percentages = re.findall(percentage_pattern, html)
    
    # Verify we found some percentages
    assert len(percentages) > 0, "Should find percentage values in the page"
    
    # Check each percentage has exactly 2 decimal places
    two_decimal_pattern = r'^\d+\.\d{2}%$'
    for pct in percentages:
        assert re.match(two_decimal_pattern, pct), f"Percentage '{pct}' should have exactly 2 decimal places"


@pytest.mark.analysis
def test_all_percentages_have_consistent_format():
    """Test that all percentages follow the XX.XX% format consistently."""
    from app import create_app
    
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'Test Q1', 'query': 'SELECT 1', 'answer': 100},
            'q2': {'question': 'International students', 'query': 'SELECT 2', 'answer': '45.67%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Another percentage', 'query': 'SELECT 5', 'answer': '78.90%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Third percentage', 'query': 'SELECT 10', 'answer': '12.34%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    
    # Find all percentage patterns
    all_percent_patterns = re.findall(r'\d+\.?\d*%', html)
    
    # Every percentage should have exactly 2 decimal places
    for pct_str in all_percent_patterns:
        # Extract just the numeric part before %
        numeric_part = pct_str[:-1]  # Remove %
        
        # Should contain a decimal point
        assert '.' in numeric_part, f"Percentage {pct_str} should have decimal point"
        
        # Should have exactly 2 digits after decimal
        decimal_places = len(numeric_part.split('.')[1])
        assert decimal_places == 2, f"Percentage {pct_str} should have exactly 2 decimal places, has {decimal_places}"


@pytest.mark.analysis
def test_analysis_items_are_labeled():
    """Test that analysis items have proper labeling structure."""
    from app import create_app
    
    def mock_query(dbname=None):
        return {
            'q1': {'question': 'How many entries?', 'query': 'SELECT 1', 'answer': 150},
            'q2': {'question': 'What percentage?', 'query': 'SELECT 2', 'answer': '55.00%'},
            'q3': {'question': 'Test Q3', 'query': 'SELECT 3', 'answer': {'avg_gpa': 3.5, 'avg_gre': 320, 'avg_gre_v': 160, 'avg_gre_aw': 4.0}},
            'q4': {'question': 'Test Q4', 'query': 'SELECT 4', 'answer': 3.7},
            'q5': {'question': 'Test Q5', 'query': 'SELECT 5', 'answer': '75.50%'},
            'q6': {'question': 'Test Q6', 'query': 'SELECT 6', 'answer': 3.6},
            'q7': {'question': 'Test Q7', 'query': 'SELECT 7', 'answer': 200},
            'q8': {'question': 'Test Q8', 'query': 'SELECT 8', 'answer': 50},
            'q9': {'question': 'Test Q9', 'query': 'SELECT 9', 'answer': 48},
            'q10': {'question': 'Test Q10', 'query': 'SELECT 10', 'answer': '60.25%'},
            'q11': {'question': 'Test Q11', 'query': 'SELECT 11', 'answer': [['MIT', 3.8, 10]]}
        }
    
    def mock_status():
        return {'is_running': False, 'status_message': 'Ready'}
    
    app = create_app(query_func=mock_query)
    client = app.test_client()
    
    response = client.get('/analysis')
    html = response.data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check that answer boxes contain answer values
    answer_boxes = soup.find_all(class_='answer-box')
    assert len(answer_boxes) > 0, "Should have answer boxes"
    
    # Check that answer values are present
    answer_values = soup.find_all(class_='answer-value')
    assert len(answer_values) > 0, "Should have answer values"
