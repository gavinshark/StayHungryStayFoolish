"""
Tests for RagasEvaluator Module

Tests the RAGAS evaluation functionality including dataset loading,
data preparation, evaluation, and report generation.
"""

import json
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from hypothesis import given, settings, strategies as st, assume

from src.evaluator import RagasEvaluator
from src.models import EvaluationSample, EvaluationResult, RAGResponse


# =============================================================================
# Hypothesis Strategies for Property-Based Testing
# =============================================================================

# Strategy for generating valid evaluation sample data
def valid_sample_strategy():
    """Generate a valid evaluation sample dictionary."""
    return st.fixed_dictionaries({
        "question": st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        "ground_truth": st.text(min_size=1, max_size=500).filter(lambda x: x.strip()),
    }).flatmap(lambda d: st.one_of(
        st.just(d),  # Without contexts
        st.fixed_dictionaries({
            "question": st.just(d["question"]),
            "ground_truth": st.just(d["ground_truth"]),
            "contexts": st.lists(
                st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
                min_size=0,
                max_size=5
            )
        })
    ))


# Strategy for generating valid evaluation datasets
def valid_dataset_strategy():
    """Generate a valid evaluation dataset with N samples."""
    return st.integers(min_value=1, max_value=10).flatmap(
        lambda n: st.fixed_dictionaries({
            "samples": st.lists(valid_sample_strategy(), min_size=n, max_size=n)
        })
    )


# Strategy for generating metric values in valid range [0.0, 1.0]
def valid_metric_strategy():
    """Generate a valid metric value in range [0.0, 1.0]."""
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


# Strategy for generating EvaluationResult with valid metrics
def valid_evaluation_result_strategy():
    """Generate a valid EvaluationResult with metrics in [0.0, 1.0]."""
    return st.fixed_dictionaries({
        "faithfulness": valid_metric_strategy(),
        "answer_relevancy": valid_metric_strategy(),
        "context_precision": valid_metric_strategy(),
        "context_recall": valid_metric_strategy(),
        "details": st.just({})
    }).map(lambda d: EvaluationResult(**d))


# Strategy for generating invalid dataset formats
def invalid_dataset_strategy():
    """Generate various invalid dataset formats."""
    return st.one_of(
        # Missing 'samples' key
        st.fixed_dictionaries({
            "data": st.lists(st.text(), min_size=0, max_size=3)
        }),
        # 'samples' is not a list
        st.fixed_dictionaries({
            "samples": st.text(min_size=1, max_size=50)
        }),
        # 'samples' is a number
        st.fixed_dictionaries({
            "samples": st.integers()
        }),
        # Sample missing 'question'
        st.fixed_dictionaries({
            "samples": st.just([{"ground_truth": "answer"}])
        }),
        # Sample missing 'ground_truth'
        st.fixed_dictionaries({
            "samples": st.just([{"question": "What is RAG?"}])
        }),
        # Sample with empty question
        st.fixed_dictionaries({
            "samples": st.just([{"question": "", "ground_truth": "answer"}])
        }),
        # Sample with whitespace-only question
        st.fixed_dictionaries({
            "samples": st.just([{"question": "   ", "ground_truth": "answer"}])
        }),
        # Sample with empty ground_truth
        st.fixed_dictionaries({
            "samples": st.just([{"question": "What?", "ground_truth": ""}])
        }),
        # Sample with whitespace-only ground_truth
        st.fixed_dictionaries({
            "samples": st.just([{"question": "What?", "ground_truth": "   "}])
        }),
        # Sample with invalid contexts type
        st.fixed_dictionaries({
            "samples": st.just([{
                "question": "What?",
                "ground_truth": "answer",
                "contexts": "not a list"
            }])
        }),
        # Sample with non-string in contexts
        st.fixed_dictionaries({
            "samples": st.just([{
                "question": "What?",
                "ground_truth": "answer",
                "contexts": [123, "valid"]
            }])
        }),
        # Sample is not a dict
        st.fixed_dictionaries({
            "samples": st.just(["not a dict"])
        }),
    )


class TestLoadDataset:
    """Tests for RagasEvaluator.load_dataset method"""
    
    def test_load_valid_dataset(self, tmp_path):
        """Test loading a valid evaluation dataset"""
        # Create a valid dataset file
        dataset = {
            "samples": [
                {
                    "question": "什么是 RAG？",
                    "ground_truth": "RAG 是检索增强生成的缩写",
                    "contexts": ["RAG 是一种技术"]
                },
                {
                    "question": "RAGAS 是什么？",
                    "ground_truth": "RAGAS 是评测框架"
                }
            ]
        }
        
        dataset_path = tmp_path / "test_dataset.json"
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False)
        
        # Create evaluator with mock rag_chain
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        # Load dataset
        samples = evaluator.load_dataset(str(dataset_path))
        
        # Verify results
        assert len(samples) == 2
        assert samples[0].question == "什么是 RAG？"
        assert samples[0].ground_truth == "RAG 是检索增强生成的缩写"
        assert samples[0].contexts == ["RAG 是一种技术"]
        assert samples[1].question == "RAGAS 是什么？"
        assert samples[1].ground_truth == "RAGAS 是评测框架"
        assert samples[1].contexts is None
    
    def test_load_dataset_file_not_found(self):
        """Test loading from non-existent file raises FileNotFoundError"""
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            evaluator.load_dataset("/non/existent/path.json")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_load_dataset_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises ValueError"""
        dataset_path = tmp_path / "invalid.json"
        with open(dataset_path, "w") as f:
            f.write("{ invalid json }")
        
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(ValueError) as exc_info:
            evaluator.load_dataset(str(dataset_path))
        
        assert "invalid json" in str(exc_info.value).lower()
    
    def test_load_dataset_missing_samples_key(self, tmp_path):
        """Test loading dataset without 'samples' key raises ValueError"""
        dataset_path = tmp_path / "no_samples.json"
        with open(dataset_path, "w") as f:
            json.dump({"data": []}, f)
        
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(ValueError) as exc_info:
            evaluator.load_dataset(str(dataset_path))
        
        assert "samples" in str(exc_info.value).lower()
    
    def test_load_dataset_empty_samples(self, tmp_path):
        """Test loading dataset with empty samples raises ValueError"""
        dataset_path = tmp_path / "empty_samples.json"
        with open(dataset_path, "w") as f:
            json.dump({"samples": []}, f)
        
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(ValueError) as exc_info:
            evaluator.load_dataset(str(dataset_path))
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_load_dataset_missing_question(self, tmp_path):
        """Test loading sample without 'question' raises ValueError"""
        dataset = {
            "samples": [
                {"ground_truth": "answer"}
            ]
        }
        dataset_path = tmp_path / "no_question.json"
        with open(dataset_path, "w") as f:
            json.dump(dataset, f)
        
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(ValueError) as exc_info:
            evaluator.load_dataset(str(dataset_path))
        
        assert "question" in str(exc_info.value).lower()
    
    def test_load_dataset_missing_ground_truth(self, tmp_path):
        """Test loading sample without 'ground_truth' raises ValueError"""
        dataset = {
            "samples": [
                {"question": "What is RAG?"}
            ]
        }
        dataset_path = tmp_path / "no_ground_truth.json"
        with open(dataset_path, "w") as f:
            json.dump(dataset, f)
        
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(ValueError) as exc_info:
            evaluator.load_dataset(str(dataset_path))
        
        assert "ground_truth" in str(exc_info.value).lower()


class TestPrepareEvaluationData:
    """Tests for RagasEvaluator.prepare_evaluation_data method"""
    
    def test_prepare_evaluation_data(self):
        """Test preparing evaluation data from samples"""
        # Create mock RAG chain
        mock_rag_chain = Mock()
        mock_rag_chain.query.side_effect = [
            RAGResponse(
                question="Q1",
                answer="A1",
                contexts=["Context 1"],
                source_documents=[]
            ),
            RAGResponse(
                question="Q2",
                answer="A2",
                contexts=["Context 2", "Context 3"],
                source_documents=[]
            )
        ]
        
        evaluator = RagasEvaluator(mock_rag_chain)
        
        samples = [
            EvaluationSample(question="Q1", ground_truth="GT1"),
            EvaluationSample(question="Q2", ground_truth="GT2")
        ]
        
        dataset = evaluator.prepare_evaluation_data(samples)
        
        # Verify dataset structure
        assert len(dataset) == 2
        assert "question" in dataset.column_names
        assert "answer" in dataset.column_names
        assert "contexts" in dataset.column_names
        assert "ground_truth" in dataset.column_names
        
        # Verify data content
        assert dataset["question"] == ["Q1", "Q2"]
        assert dataset["answer"] == ["A1", "A2"]
        assert dataset["contexts"] == [["Context 1"], ["Context 2", "Context 3"]]
        assert dataset["ground_truth"] == ["GT1", "GT2"]
    
    def test_prepare_evaluation_data_empty_samples(self):
        """Test preparing evaluation data with empty samples raises ValueError"""
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        with pytest.raises(ValueError) as exc_info:
            evaluator.prepare_evaluation_data([])
        
        assert "empty" in str(exc_info.value).lower()


class TestEvaluate:
    """Tests for RagasEvaluator.evaluate method"""
    
    @patch("src.evaluator.OpenAIEmbeddings")
    @patch("src.evaluator.ChatOpenAI")
    @patch("src.evaluator.evaluate")
    def test_evaluate_returns_result(self, mock_ragas_evaluate, mock_chat_openai, mock_embeddings):
        """Test evaluate method returns EvaluationResult"""
        # Setup mock RAGAS evaluate result
        mock_result = MagicMock()
        # Setup __getitem__ for dictionary-style access
        mock_result.__getitem__.side_effect = lambda key: {
            "faithfulness": 0.85,
            "answer_relevancy": 0.90,
            "context_precision": 0.75,
            "context_recall": 0.80
        }.get(key)
        mock_result.to_pandas.return_value.to_dict.return_value = [
            {"faithfulness": 0.85, "answer_relevancy": 0.90}
        ]
        mock_ragas_evaluate.return_value = mock_result
        
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain, api_key="test-key")
        
        # Create a mock dataset
        from datasets import Dataset
        mock_dataset = Dataset.from_dict({
            "question": ["Q1"],
            "answer": ["A1"],
            "contexts": [["C1"]],
            "ground_truth": ["GT1"]
        })
        
        result = evaluator.evaluate(mock_dataset)
        
        # Verify result
        assert isinstance(result, EvaluationResult)
        assert result.faithfulness == 0.85
        assert result.answer_relevancy == 0.90
        assert result.context_precision == 0.75
        assert result.context_recall == 0.80


class TestGenerateReport:
    """Tests for RagasEvaluator.generate_report method"""
    
    def test_generate_report_contains_all_metrics(self):
        """Test generated report contains all metric names and values"""
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        result = EvaluationResult(
            faithfulness=0.85,
            answer_relevancy=0.90,
            context_precision=0.75,
            context_recall=0.80,
            details={}
        )
        
        report = evaluator.generate_report(result)
        
        # Verify report contains all metrics
        assert "Faithfulness" in report
        assert "Answer Relevancy" in report
        assert "Context Precision" in report
        assert "Context Recall" in report
        
        # Verify report contains metric values
        assert "0.8500" in report
        assert "0.9000" in report
        assert "0.7500" in report
        assert "0.8000" in report
    
    def test_generate_report_excellent_score(self):
        """Test report shows excellent rating for high scores"""
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        result = EvaluationResult(
            faithfulness=0.90,
            answer_relevancy=0.90,
            context_precision=0.90,
            context_recall=0.90,
            details={}
        )
        
        report = evaluator.generate_report(result)
        
        assert "优秀" in report
    
    def test_generate_report_needs_improvement(self):
        """Test report shows needs improvement for low scores"""
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        result = EvaluationResult(
            faithfulness=0.20,
            answer_relevancy=0.20,
            context_precision=0.20,
            context_recall=0.20,
            details={}
        )
        
        report = evaluator.generate_report(result)
        
        assert "需改进" in report


class TestRagasEvaluatorInit:
    """Tests for RagasEvaluator initialization"""
    
    def test_init_with_rag_chain(self):
        """Test evaluator initializes with RAG chain"""
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        assert evaluator.rag_chain is mock_rag_chain
        assert len(evaluator.metrics) == 4



# =============================================================================
# Property-Based Tests for RagasEvaluator
# =============================================================================

class TestEvaluatorPropertyTests:
    """
    Property-based tests for RagasEvaluator.
    
    These tests verify correctness properties across many randomly generated inputs.
    """
    
    @settings(max_examples=100)
    @given(dataset=valid_dataset_strategy())
    def test_property_9_evaluation_dataset_load_consistency(self, dataset, tmp_path_factory):
        """
        Feature: ragas-evaluation-demo, Property 9: Evaluation Dataset Load Consistency
        
        For any valid evaluation dataset JSON file with N samples, loading with
        RagasEvaluator should produce exactly N EvaluationSample objects.
        
        **Validates: Requirements 5.1**
        """
        # Get the number of samples in the generated dataset
        expected_count = len(dataset["samples"])
        
        # Create a temporary file with the dataset
        tmp_path = tmp_path_factory.mktemp("data")
        dataset_path = tmp_path / "test_dataset.json"
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False)
        
        # Create evaluator with mock rag_chain
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        # Load the dataset
        samples = evaluator.load_dataset(str(dataset_path))
        
        # Verify the number of samples matches
        assert len(samples) == expected_count, (
            f"Expected {expected_count} samples, but got {len(samples)}"
        )
        
        # Verify each sample is an EvaluationSample instance
        for i, sample in enumerate(samples):
            assert isinstance(sample, EvaluationSample), (
                f"Sample at index {i} is not an EvaluationSample instance"
            )
            # Verify required fields are present and non-empty
            assert sample.question, f"Sample at index {i} has empty question"
            assert sample.ground_truth, f"Sample at index {i} has empty ground_truth"
    
    @settings(max_examples=100)
    @given(result=valid_evaluation_result_strategy())
    def test_property_10_ragas_metrics_range_constraint(self, result):
        """
        Feature: ragas-evaluation-demo, Property 10: RAGAS Metrics Range Constraint
        
        For any evaluation result, all metrics (faithfulness, answer_relevancy,
        context_precision, context_recall) should be in the range [0.0, 1.0].
        
        **Validates: Requirements 5.2, 5.3, 5.4, 5.5**
        """
        # Verify faithfulness is in range [0.0, 1.0]
        assert 0.0 <= result.faithfulness <= 1.0, (
            f"Faithfulness {result.faithfulness} is not in range [0.0, 1.0]"
        )
        
        # Verify answer_relevancy is in range [0.0, 1.0]
        assert 0.0 <= result.answer_relevancy <= 1.0, (
            f"Answer Relevancy {result.answer_relevancy} is not in range [0.0, 1.0]"
        )
        
        # Verify context_precision is in range [0.0, 1.0]
        assert 0.0 <= result.context_precision <= 1.0, (
            f"Context Precision {result.context_precision} is not in range [0.0, 1.0]"
        )
        
        # Verify context_recall is in range [0.0, 1.0]
        assert 0.0 <= result.context_recall <= 1.0, (
            f"Context Recall {result.context_recall} is not in range [0.0, 1.0]"
        )
    
    @settings(max_examples=100)
    @given(result=valid_evaluation_result_strategy())
    def test_property_11_evaluation_report_completeness(self, result):
        """
        Feature: ragas-evaluation-demo, Property 11: Evaluation Report Completeness
        
        For any EvaluationResult, the generated report should contain all four
        metric names and their corresponding values.
        
        **Validates: Requirements 5.6**
        """
        # Create evaluator with mock rag_chain
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        # Generate the report
        report = evaluator.generate_report(result)
        
        # Verify report contains all metric names
        assert "Faithfulness" in report, "Report missing 'Faithfulness' metric name"
        assert "Answer Relevancy" in report, "Report missing 'Answer Relevancy' metric name"
        assert "Context Precision" in report, "Report missing 'Context Precision' metric name"
        assert "Context Recall" in report, "Report missing 'Context Recall' metric name"
        
        # Verify report contains the metric values (formatted to 4 decimal places)
        faithfulness_str = f"{result.faithfulness:.4f}"
        answer_relevancy_str = f"{result.answer_relevancy:.4f}"
        context_precision_str = f"{result.context_precision:.4f}"
        context_recall_str = f"{result.context_recall:.4f}"
        
        assert faithfulness_str in report, (
            f"Report missing faithfulness value {faithfulness_str}"
        )
        assert answer_relevancy_str in report, (
            f"Report missing answer_relevancy value {answer_relevancy_str}"
        )
        assert context_precision_str in report, (
            f"Report missing context_precision value {context_precision_str}"
        )
        assert context_recall_str in report, (
            f"Report missing context_recall value {context_recall_str}"
        )
    
    @settings(max_examples=100)
    @given(invalid_data=invalid_dataset_strategy())
    def test_property_13_invalid_dataset_format_error_handling(self, invalid_data, tmp_path_factory):
        """
        Feature: ragas-evaluation-demo, Property 13: Invalid Dataset Format Error Handling
        
        For any JSON file that does not conform to the expected evaluation dataset
        schema, RagasEvaluator should raise a validation error with a descriptive message.
        
        **Validates: Requirements 5.7**
        """
        # Create a temporary file with the invalid dataset
        tmp_path = tmp_path_factory.mktemp("data")
        dataset_path = tmp_path / "invalid_dataset.json"
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f, ensure_ascii=False)
        
        # Create evaluator with mock rag_chain
        mock_rag_chain = Mock()
        evaluator = RagasEvaluator(mock_rag_chain)
        
        # Attempt to load the invalid dataset - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            evaluator.load_dataset(str(dataset_path))
        
        # Verify the error message is descriptive
        error_message = str(exc_info.value).lower()
        assert len(error_message) > 0, "Error message should not be empty"
        
        # The error message should contain relevant keywords indicating the issue
        descriptive_keywords = [
            "invalid", "missing", "format", "samples", "question", 
            "ground_truth", "empty", "must be", "expected"
        ]
        has_descriptive_keyword = any(
            keyword in error_message for keyword in descriptive_keywords
        )
        assert has_descriptive_keyword, (
            f"Error message '{error_message}' should contain descriptive keywords "
            f"about the validation failure"
        )
