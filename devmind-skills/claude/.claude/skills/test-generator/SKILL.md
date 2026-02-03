---
name: generate-tests
description: Generate comprehensive unit tests with edge cases, mocks, fixtures, and parameterized tests. Use this when asked to create tests, write unit tests, generate test coverage, or add tests for a function/class.
---

# Test Generator Skill

You are a **senior test engineer** writing production-quality tests. Your tests are comprehensive, maintainable, and follow testing best practices.

## Execution Strategy

### Phase 1: Code Analysis

Before generating tests, analyze the target code:

1. **Identify testable units:**
   - Public functions and methods
   - Class constructors and properties
   - Module-level functions
   - API endpoints

2. **Identify dependencies to mock:**
   - Database connections
   - External API calls
   - File system operations
   - Time/date functions
   - Random number generators

3. **Identify test scenarios:**
   - Happy path (normal success cases)
   - Edge cases (boundaries, empty, null)
   - Error cases (exceptions, invalid input)
   - Integration points

### Phase 2: Test Categories

#### Category 1: Happy Path Tests
Test normal, expected behavior:
```
□ Valid inputs produce expected outputs
□ Multiple valid input variations
□ State changes correctly
□ Return values are correct type and format
□ Side effects occur as expected
```

#### Category 2: Edge Case Tests
Test boundary conditions:
```
□ Empty inputs (empty string, empty list, empty dict)
□ Null/None inputs
□ Single element collections
□ Maximum size inputs
□ Boundary values (0, -1, MAX_INT, MIN_INT)
□ Unicode and special characters
□ Whitespace handling
□ Very long strings
□ Deeply nested structures
```

#### Category 3: Error Case Tests
Test error handling:
```
□ Invalid input types
□ Missing required parameters
□ Out-of-range values
□ Malformed data
□ Network/IO failures (for integration points)
□ Timeout scenarios
□ Permission errors
□ Resource exhaustion
```

#### Category 4: Integration Tests
Test component interactions:
```
□ Database operations
□ External API calls
□ File system operations
□ Cache behavior
□ Message queue interactions
```

### Phase 3: Framework-Specific Templates

#### Python (pytest)

```python
"""Tests for {module_name}.

This module contains comprehensive unit tests for the {module_name} module,
covering happy paths, edge cases, and error scenarios.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
import json

from {module_path} import {ClassName, function_name}


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": datetime(2024, 1, 1, 12, 0, 0)
    }


@pytest.fixture
def mock_database():
    """Create a mock database connection."""
    mock_db = Mock()
    mock_db.query.return_value = []
    mock_db.commit.return_value = None
    return mock_db


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    with patch("httpx.Client") as mock:
        client = Mock()
        mock.return_value.__enter__ = Mock(return_value=client)
        mock.return_value.__exit__ = Mock(return_value=False)
        yield client


# =============================================================================
# Tests for ClassName
# =============================================================================

class TestClassName:
    """Tests for the ClassName class."""

    # -------------------------------------------------------------------------
    # Initialization Tests
    # -------------------------------------------------------------------------
    
    def test_init_with_valid_params(self):
        """Test initialization with valid parameters."""
        instance = ClassName(param1="value1", param2=42)
        
        assert instance.param1 == "value1"
        assert instance.param2 == 42
        assert instance.is_initialized is True

    def test_init_with_defaults(self):
        """Test initialization uses correct default values."""
        instance = ClassName()
        
        assert instance.param1 == "default_value"
        assert instance.param2 == 0

    def test_init_with_invalid_type_raises_type_error(self):
        """Test initialization with wrong type raises TypeError."""
        with pytest.raises(TypeError, match="param1 must be a string"):
            ClassName(param1=123)

    # -------------------------------------------------------------------------
    # Method Tests: Happy Path
    # -------------------------------------------------------------------------
    
    def test_method_returns_expected_result(self, sample_user):
        """Test method returns correct result for valid input."""
        instance = ClassName()
        
        result = instance.process(sample_user)
        
        assert result["status"] == "success"
        assert result["user_id"] == sample_user["id"]

    def test_method_handles_multiple_items(self):
        """Test method correctly processes multiple items."""
        instance = ClassName()
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        results = instance.process_batch(items)
        
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)

    # -------------------------------------------------------------------------
    # Method Tests: Edge Cases
    # -------------------------------------------------------------------------
    
    def test_method_with_empty_input(self):
        """Test method handles empty input gracefully."""
        instance = ClassName()
        
        result = instance.process([])
        
        assert result == []

    def test_method_with_none_input(self):
        """Test method handles None input appropriately."""
        instance = ClassName()
        
        with pytest.raises(ValueError, match="Input cannot be None"):
            instance.process(None)

    def test_method_with_unicode_characters(self):
        """Test method handles unicode characters correctly."""
        instance = ClassName()
        unicode_input = {"name": "日本語テスト", "emoji": "🎉"}
        
        result = instance.process(unicode_input)
        
        assert result["name"] == "日本語テスト"

    def test_method_with_max_length_string(self):
        """Test method handles maximum length strings."""
        instance = ClassName()
        max_string = "x" * 10000
        
        result = instance.process({"data": max_string})
        
        assert len(result["data"]) == 10000

    # -------------------------------------------------------------------------
    # Method Tests: Error Cases
    # -------------------------------------------------------------------------
    
    def test_method_raises_on_invalid_format(self):
        """Test method raises exception for invalid input format."""
        instance = ClassName()
        
        with pytest.raises(ValueError) as exc_info:
            instance.process({"invalid": "format"})
        
        assert "Missing required field" in str(exc_info.value)

    # -------------------------------------------------------------------------
    # Integration Tests with Mocks
    # -------------------------------------------------------------------------
    
    def test_method_calls_database_correctly(self, mock_database):
        """Test method interacts with database correctly."""
        instance = ClassName(db=mock_database)
        
        instance.save({"id": 1, "name": "test"})
        
        mock_database.query.assert_called_once()
        mock_database.commit.assert_called_once()

    @patch("module.external_api.fetch")
    def test_method_handles_api_timeout(self, mock_fetch):
        """Test method handles API timeout gracefully."""
        mock_fetch.side_effect = TimeoutError("Connection timed out")
        instance = ClassName()
        
        result = instance.fetch_external_data()
        
        assert result["status"] == "error"
        assert "timeout" in result["message"].lower()


# =============================================================================
# Tests for function_name
# =============================================================================

class TestFunctionName:
    """Tests for the function_name function."""

    @pytest.mark.parametrize("input_val,expected", [
        ("valid", True),
        ("also_valid", True),
        ("", False),
        (None, False),
        ("   ", False),  # Whitespace only
        ("a", True),      # Single character
    ])
    def test_function_with_various_inputs(self, input_val, expected):
        """Test function with various input scenarios."""
        result = function_name(input_val)
        assert result == expected

    @pytest.mark.parametrize("num,expected", [
        (0, "zero"),
        (1, "positive"),
        (-1, "negative"),
        (999999999, "positive"),
        (-999999999, "negative"),
    ])
    def test_function_boundary_values(self, num, expected):
        """Test function with boundary values."""
        result = function_name(num)
        assert result == expected


# =============================================================================
# Async Tests
# =============================================================================

class TestAsyncFunctions:
    """Tests for async functions."""

    @pytest.mark.asyncio
    async def test_async_function_returns_result(self):
        """Test async function returns expected result."""
        result = await async_function("input")
        
        assert result["status"] == "complete"

    @pytest.mark.asyncio
    async def test_async_function_with_mock(self):
        """Test async function with mocked dependency."""
        with patch("module.async_client.fetch", new_callable=AsyncMock) as mock:
            mock.return_value = {"data": "mocked"}
            
            result = await async_function("input")
            
            mock.assert_awaited_once()
            assert result["data"] == "mocked"

    @pytest.mark.asyncio
    async def test_async_function_handles_exception(self):
        """Test async function exception handling."""
        with pytest.raises(ValueError):
            await async_function(None)
```

#### TypeScript/JavaScript (Jest/Vitest)

```typescript
/**
 * Tests for {module_name}
 * 
 * Comprehensive unit tests covering happy paths, edge cases, and error scenarios.
 */

import { describe, it, expect, beforeEach, afterEach, vi, Mock } from 'vitest';
// For Jest use: import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';

import { ClassName, functionName } from './module';
import { ExternalService } from './services/external';

// =============================================================================
// Mocks
// =============================================================================

vi.mock('./services/external', () => ({
  ExternalService: {
    fetch: vi.fn(),
    save: vi.fn(),
  },
}));

// =============================================================================
// Test Utilities
// =============================================================================

const createSampleUser = (overrides = {}) => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  createdAt: new Date('2024-01-01'),
  ...overrides,
});

// =============================================================================
// Tests for ClassName
// =============================================================================

describe('ClassName', () => {
  let instance: ClassName;

  beforeEach(() => {
    instance = new ClassName();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  // ---------------------------------------------------------------------------
  // Constructor Tests
  // ---------------------------------------------------------------------------
  
  describe('constructor', () => {
    it('should initialize with valid parameters', () => {
      const instance = new ClassName({ param1: 'value', param2: 42 });
      
      expect(instance.param1).toBe('value');
      expect(instance.param2).toBe(42);
    });

    it('should use default values when not provided', () => {
      const instance = new ClassName();
      
      expect(instance.param1).toBe('default');
      expect(instance.param2).toBe(0);
    });

    it('should throw for invalid parameter types', () => {
      expect(() => new ClassName({ param1: 123 as any }))
        .toThrow(TypeError);
    });
  });

  // ---------------------------------------------------------------------------
  // Method Tests: Happy Path
  // ---------------------------------------------------------------------------
  
  describe('process', () => {
    it('should return expected result for valid input', () => {
      const user = createSampleUser();
      
      const result = instance.process(user);
      
      expect(result).toEqual({
        status: 'success',
        userId: user.id,
      });
    });

    it('should handle multiple items correctly', () => {
      const items = [{ id: 1 }, { id: 2 }, { id: 3 }];
      
      const results = instance.processBatch(items);
      
      expect(results).toHaveLength(3);
      expect(results.every(r => r.status === 'success')).toBe(true);
    });
  });

  // ---------------------------------------------------------------------------
  // Edge Case Tests
  // ---------------------------------------------------------------------------
  
  describe('edge cases', () => {
    it('should handle empty input', () => {
      const result = instance.process([]);
      expect(result).toEqual([]);
    });

    it('should handle null input', () => {
      expect(() => instance.process(null)).toThrow('Input cannot be null');
    });

    it('should handle undefined input', () => {
      expect(() => instance.process(undefined)).toThrow('Input is required');
    });

    it('should handle unicode characters', () => {
      const input = { name: '日本語テスト', emoji: '🎉' };
      
      const result = instance.process(input);
      
      expect(result.name).toBe('日本語テスト');
    });

    it('should handle very long strings', () => {
      const longString = 'x'.repeat(10000);
      
      const result = instance.process({ data: longString });
      
      expect(result.data.length).toBe(10000);
    });
  });

  // ---------------------------------------------------------------------------
  // Error Case Tests
  // ---------------------------------------------------------------------------
  
  describe('error handling', () => {
    it('should throw for invalid format', () => {
      expect(() => instance.process({ invalid: 'format' }))
        .toThrow('Missing required field');
    });

    it('should handle API timeout gracefully', async () => {
      (ExternalService.fetch as Mock).mockRejectedValue(
        new Error('Connection timed out')
      );
      
      const result = await instance.fetchExternalData();
      
      expect(result.status).toBe('error');
      expect(result.message).toContain('timeout');
    });
  });

  // ---------------------------------------------------------------------------
  // Integration Tests with Mocks
  // ---------------------------------------------------------------------------
  
  describe('integration', () => {
    it('should call external service correctly', async () => {
      (ExternalService.fetch as Mock).mockResolvedValue({ data: 'result' });
      
      await instance.fetchAndProcess();
      
      expect(ExternalService.fetch).toHaveBeenCalledTimes(1);
      expect(ExternalService.fetch).toHaveBeenCalledWith(
        expect.objectContaining({ id: expect.any(Number) })
      );
    });
  });
});

// =============================================================================
// Tests for functionName
// =============================================================================

describe('functionName', () => {
  it.each([
    ['valid', true],
    ['also_valid', true],
    ['', false],
    [null, false],
    ['   ', false],
    ['a', true],
  ])('should return %s for input "%s"', (input, expected) => {
    expect(functionName(input)).toBe(expected);
  });

  it.each([
    [0, 'zero'],
    [1, 'positive'],
    [-1, 'negative'],
    [Number.MAX_SAFE_INTEGER, 'positive'],
    [Number.MIN_SAFE_INTEGER, 'negative'],
  ])('should handle boundary value %i', (num, expected) => {
    expect(functionName(num)).toBe(expected);
  });
});

// =============================================================================
// Async Tests
// =============================================================================

describe('async functions', () => {
  it('should resolve with expected result', async () => {
    const result = await asyncFunction('input');
    
    expect(result.status).toBe('complete');
  });

  it('should reject for invalid input', async () => {
    await expect(asyncFunction(null)).rejects.toThrow(ValueError);
  });
});
```

#### Go (testing)

```go
package module_test

import (
    "context"
    "errors"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/require"
    
    "your/module"
)

// =============================================================================
// Mocks
// =============================================================================

type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) Query(ctx context.Context, query string, args ...interface{}) ([]interface{}, error) {
    arguments := m.Called(ctx, query, args)
    return arguments.Get(0).([]interface{}), arguments.Error(1)
}

func (m *MockDatabase) Save(ctx context.Context, data interface{}) error {
    arguments := m.Called(ctx, data)
    return arguments.Error(0)
}

// =============================================================================
// Test Fixtures
// =============================================================================

func createSampleUser() *module.User {
    return &module.User{
        ID:        1,
        Username:  "testuser",
        Email:     "test@example.com",
        CreatedAt: time.Date(2024, 1, 1, 12, 0, 0, 0, time.UTC),
    }
}

// =============================================================================
// Tests for ClassName
// =============================================================================

func TestClassName_New(t *testing.T) {
    t.Run("creates instance with valid params", func(t *testing.T) {
        instance, err := module.NewClassName("value", 42)
        
        require.NoError(t, err)
        assert.Equal(t, "value", instance.Param1)
        assert.Equal(t, 42, instance.Param2)
    })

    t.Run("uses defaults when params not provided", func(t *testing.T) {
        instance, err := module.NewClassName("", 0)
        
        require.NoError(t, err)
        assert.Equal(t, "default", instance.Param1)
    })

    t.Run("returns error for invalid params", func(t *testing.T) {
        _, err := module.NewClassName("", -1)
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "invalid param2")
    })
}

func TestClassName_Process(t *testing.T) {
    // Happy path tests
    t.Run("returns expected result for valid input", func(t *testing.T) {
        instance, _ := module.NewClassName("test", 1)
        user := createSampleUser()
        
        result, err := instance.Process(user)
        
        require.NoError(t, err)
        assert.Equal(t, "success", result.Status)
        assert.Equal(t, user.ID, result.UserID)
    })

    // Edge case tests
    t.Run("handles nil input", func(t *testing.T) {
        instance, _ := module.NewClassName("test", 1)
        
        _, err := instance.Process(nil)
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "input cannot be nil")
    })

    t.Run("handles empty struct", func(t *testing.T) {
        instance, _ := module.NewClassName("test", 1)
        
        result, err := instance.Process(&module.User{})
        
        require.NoError(t, err)
        assert.Equal(t, int64(0), result.UserID)
    })
}

// =============================================================================
// Table-Driven Tests
// =============================================================================

func TestFunctionName(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected bool
        wantErr  bool
    }{
        {
            name:     "valid input returns true",
            input:    "valid",
            expected: true,
            wantErr:  false,
        },
        {
            name:     "empty input returns false",
            input:    "",
            expected: false,
            wantErr:  false,
        },
        {
            name:     "whitespace only returns false",
            input:    "   ",
            expected: false,
            wantErr:  false,
        },
        {
            name:     "unicode characters handled",
            input:    "日本語",
            expected: true,
            wantErr:  false,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := module.FunctionName(tt.input)
            
            if tt.wantErr {
                assert.Error(t, err)
                return
            }
            
            require.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}

// =============================================================================
// Integration Tests with Mocks
// =============================================================================

func TestClassName_WithDatabase(t *testing.T) {
    t.Run("calls database correctly", func(t *testing.T) {
        mockDB := new(MockDatabase)
        mockDB.On("Save", mock.Anything, mock.Anything).Return(nil)
        
        instance := module.NewClassNameWithDB(mockDB)
        data := map[string]interface{}{"id": 1, "name": "test"}
        
        err := instance.Save(context.Background(), data)
        
        require.NoError(t, err)
        mockDB.AssertCalled(t, "Save", mock.Anything, data)
    })

    t.Run("handles database error", func(t *testing.T) {
        mockDB := new(MockDatabase)
        mockDB.On("Save", mock.Anything, mock.Anything).Return(errors.New("connection failed"))
        
        instance := module.NewClassNameWithDB(mockDB)
        
        err := instance.Save(context.Background(), nil)
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "connection failed")
    })
}

// =============================================================================
// Benchmark Tests
// =============================================================================

func BenchmarkFunctionName(b *testing.B) {
    for i := 0; i < b.N; i++ {
        module.FunctionName("test-input")
    }
}
```

#### Java (JUnit 5)

```java
package com.example.module;

import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.LocalDateTime;
import java.util.*;

/**
 * Comprehensive unit tests for ClassName.
 * 
 * Covers happy paths, edge cases, and error scenarios.
 */
class ClassNameTest {
    
    @Mock
    private DatabaseService mockDatabase;
    
    @Mock
    private ExternalApiClient mockApiClient;
    
    @InjectMocks
    private ClassName classUnderTest;
    
    private AutoCloseable closeable;
    
    // =========================================================================
    // Setup and Teardown
    // =========================================================================
    
    @BeforeEach
    void setUp() {
        closeable = MockitoAnnotations.openMocks(this);
    }
    
    @AfterEach
    void tearDown() throws Exception {
        closeable.close();
    }
    
    // =========================================================================
    // Constructor Tests
    // =========================================================================
    
    @Test
    @DisplayName("Should initialize with valid parameters")
    void testConstructorWithValidParams() {
        ClassName instance = new ClassName("value1", 42);
        
        assertEquals("value1", instance.getParam1());
        assertEquals(42, instance.getParam2());
        assertTrue(instance.isInitialized());
    }
    
    @Test
    @DisplayName("Should use default values when not provided")
    void testConstructorWithDefaults() {
        ClassName instance = new ClassName();
        
        assertEquals("default", instance.getParam1());
        assertEquals(0, instance.getParam2());
    }
    
    @Test
    @DisplayName("Should throw IllegalArgumentException for invalid type")
    void testConstructorThrowsForInvalidType() {
        Exception exception = assertThrows(
            IllegalArgumentException.class,
            () -> new ClassName(null, -1)
        );
        
        assertTrue(exception.getMessage().contains("param1 cannot be null"));
    }
    
    // =========================================================================
    // Happy Path Tests
    // =========================================================================
    
    @Test
    @DisplayName("Process should return expected result for valid input")
    void testProcessReturnsExpectedResult() {
        User user = createSampleUser();
        
        Result result = classUnderTest.process(user);
        
        assertEquals("success", result.getStatus());
        assertEquals(user.getId(), result.getUserId());
    }
    
    @Test
    @DisplayName("ProcessBatch should handle multiple items")
    void testProcessBatchHandlesMultipleItems() {
        List<Item> items = Arrays.asList(
            new Item(1), new Item(2), new Item(3)
        );
        
        List<Result> results = classUnderTest.processBatch(items);
        
        assertEquals(3, results.size());
        assertTrue(results.stream().allMatch(r -> "success".equals(r.getStatus())));
    }
    
    // =========================================================================
    // Edge Case Tests
    // =========================================================================
    
    @Test
    @DisplayName("Process should handle empty input")
    void testProcessHandlesEmptyInput() {
        List<Item> emptyList = Collections.emptyList();
        
        List<Result> results = classUnderTest.processBatch(emptyList);
        
        assertTrue(results.isEmpty());
    }
    
    @Test
    @DisplayName("Process should handle null input")
    void testProcessHandlesNullInput() {
        Exception exception = assertThrows(
            IllegalArgumentException.class,
            () -> classUnderTest.process(null)
        );
        
        assertTrue(exception.getMessage().contains("Input cannot be null"));
    }
    
    @Test
    @DisplayName("Process should handle unicode characters")
    void testProcessHandlesUnicode() {
        User user = new User();
        user.setName("日本語テスト");
        user.setDescription("🎉");
        
        Result result = classUnderTest.process(user);
        
        assertEquals("日本語テスト", result.getUserName());
    }
    
    // =========================================================================
    // Parameterized Tests
    // =========================================================================
    
    @ParameterizedTest
    @CsvSource({
        "valid, true",
        "also_valid, true",
        "'', false",
        "' ', false"
    })
    @DisplayName("ValidateInput should return correct result for various inputs")
    void testValidateInputVariousInputs(String input, boolean expected) {
        boolean result = classUnderTest.validateInput(input);
        assertEquals(expected, result);
    }
    
    @ParameterizedTest
    @ValueSource(ints = {0, 1, -1, Integer.MAX_VALUE, Integer.MIN_VALUE})
    @DisplayName("ClassifyNumber should handle boundary values")
    void testClassifyNumberBoundaryValues(int num) {
        String result = classUnderTest.classifyNumber(num);
        assertNotNull(result);
    }
    
    // =========================================================================
    // Integration Tests with Mocks
    // =========================================================================
    
    @Test
    @DisplayName("Save should call database correctly")
    void testSaveCallsDatabaseCorrectly() {
        Map<String, Object> data = new HashMap<>();
        data.put("id", 1);
        data.put("name", "test");
        
        when(mockDatabase.save(any())).thenReturn(true);
        
        classUnderTest.save(data);
        
        verify(mockDatabase, times(1)).save(eq(data));
    }
    
    @Test
    @DisplayName("FetchExternalData should handle API timeout")
    void testFetchExternalDataHandlesTimeout() {
        when(mockApiClient.fetch())
            .thenThrow(new TimeoutException("Connection timed out"));
        
        Result result = classUnderTest.fetchExternalData();
        
        assertEquals("error", result.getStatus());
        assertTrue(result.getMessage().toLowerCase().contains("timeout"));
    }
    
    // =========================================================================
    // Helper Methods
    // =========================================================================
    
    private User createSampleUser() {
        User user = new User();
        user.setId(1L);
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        user.setCreatedAt(LocalDateTime.of(2024, 1, 1, 12, 0));
        return user;
    }
}
```

#### C# (xUnit)

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Xunit;
using Moq;
using FluentAssertions;

namespace YourNamespace.Tests
{
    /// <summary>
    /// Comprehensive unit tests for ClassName.
    /// 
    /// Covers happy paths, edge cases, and error scenarios.
    /// </summary>
    public class ClassNameTests : IDisposable
    {
        private readonly Mock<IDatabaseService> _mockDatabase;
        private readonly Mock<IExternalApiClient> _mockApiClient;
        private readonly ClassName _classUnderTest;
        
        public ClassNameTests()
        {
            _mockDatabase = new Mock<IDatabaseService>();
            _mockApiClient = new Mock<IExternalApiClient>();
            _classUnderTest = new ClassName(_mockDatabase.Object, _mockApiClient.Object);
        }
        
        public void Dispose()
        {
            // Cleanup resources
        }
        
        // =====================================================================
        // Constructor Tests
        // =====================================================================
        
        [Fact]
        public void Constructor_WithValidParameters_ShouldInitialize()
        {
            // Arrange & Act
            var instance = new ClassName("value1", 42);
            
            // Assert
            instance.Param1.Should().Be("value1");
            instance.Param2.Should().Be(42);
            instance.IsInitialized.Should().BeTrue();
        }
        
        [Fact]
        public void Constructor_WithNoParameters_ShouldUseDefaults()
        {
            // Arrange & Act
            var instance = new ClassName();
            
            // Assert
            instance.Param1.Should().Be("default");
            instance.Param2.Should().Be(0);
        }
        
        [Fact]
        public void Constructor_WithInvalidParameters_ShouldThrowArgumentException()
        {
            // Arrange & Act
            Action act = () => new ClassName(null, -1);
            
            // Assert
            act.Should().Throw<ArgumentException>()
                .WithMessage("*param1 cannot be null*");
        }
        
        // =====================================================================
        // Happy Path Tests
        // =====================================================================
        
        [Fact]
        public void Process_WithValidUser_ShouldReturnExpectedResult()
        {
            // Arrange
            var user = CreateSampleUser();
            
            // Act
            var result = _classUnderTest.Process(user);
            
            // Assert
            result.Status.Should().Be("success");
            result.UserId.Should().Be(user.Id);
        }
        
        [Fact]
        public void ProcessBatch_WithMultipleItems_ShouldHandleAll()
        {
            // Arrange
            var items = new List<Item>
            {
                new Item { Id = 1 },
                new Item { Id = 2 },
                new Item { Id = 3 }
            };
            
            // Act
            var results = _classUnderTest.ProcessBatch(items);
            
            // Assert
            results.Should().HaveCount(3);
            results.Should().OnlyContain(r => r.Status == "success");
        }
        
        // =====================================================================
        // Edge Case Tests
        // =====================================================================
        
        [Fact]
        public void Process_WithEmptyInput_ShouldReturnEmptyList()
        {
            // Arrange
            var emptyList = new List<Item>();
            
            // Act
            var results = _classUnderTest.ProcessBatch(emptyList);
            
            // Assert
            results.Should().BeEmpty();
        }
        
        [Fact]
        public void Process_WithNullInput_ShouldThrowArgumentNullException()
        {
            // Arrange & Act
            Action act = () => _classUnderTest.Process(null);
            
            // Assert
            act.Should().Throw<ArgumentNullException>()
                .WithMessage("*Input cannot be null*");
        }
        
        [Fact]
        public void Process_WithUnicodeCharacters_ShouldHandleCorrectly()
        {
            // Arrange
            var user = new User
            {
                Name = "日本語テスト",
                Description = "🎉"
            };
            
            // Act
            var result = _classUnderTest.Process(user);
            
            // Assert
            result.UserName.Should().Be("日本語テスト");
        }
        
        // =====================================================================
        // Theory Tests (Parameterized)
        // =====================================================================
        
        [Theory]
        [InlineData("valid", true)]
        [InlineData("also_valid", true)]
        [InlineData("", false)]
        [InlineData("   ", false)]
        [InlineData(null, false)]
        public void ValidateInput_WithVariousInputs_ShouldReturnExpected(
            string input, bool expected)
        {
            // Act
            var result = _classUnderTest.ValidateInput(input);
            
            // Assert
            result.Should().Be(expected);
        }
        
        [Theory]
        [InlineData(0, "zero")]
        [InlineData(1, "positive")]
        [InlineData(-1, "negative")]
        [InlineData(int.MaxValue, "positive")]
        [InlineData(int.MinValue, "negative")]
        public void ClassifyNumber_WithBoundaryValues_ShouldReturnCorrectClassification(
            int num, string expected)
        {
            // Act
            var result = _classUnderTest.ClassifyNumber(num);
            
            // Assert
            result.Should().Be(expected);
        }
        
        // =====================================================================
        // Integration Tests with Mocks
        // =====================================================================
        
        [Fact]
        public void Save_ShouldCallDatabaseCorrectly()
        {
            // Arrange
            var data = new Dictionary<string, object>
            {
                { "id", 1 },
                { "name", "test" }
            };
            
            _mockDatabase.Setup(db => db.Save(It.IsAny<Dictionary<string, object>>()))
                .Returns(true);
            
            // Act
            _classUnderTest.Save(data);
            
            // Assert
            _mockDatabase.Verify(
                db => db.Save(It.Is<Dictionary<string, object>>(d => d.Equals(data))),
                Times.Once
            );
        }
        
        [Fact]
        public async Task FetchExternalDataAsync_WithTimeout_ShouldHandleGracefully()
        {
            // Arrange
            _mockApiClient.Setup(client => client.FetchAsync())
                .ThrowsAsync(new TimeoutException("Connection timed out"));
            
            // Act
            var result = await _classUnderTest.FetchExternalDataAsync();
            
            // Assert
            result.Status.Should().Be("error");
            result.Message.Should().Contain("timeout", Substring.OrdinalIgnoreCase);
        }
        
        // =====================================================================
        // Async Tests
        // =====================================================================
        
        [Fact]
        public async Task ProcessAsync_WithValidInput_ShouldResolve()
        {
            // Arrange
            var input = "test-input";
            
            // Act
            var result = await _classUnderTest.ProcessAsync(input);
            
            // Assert
            result.Status.Should().Be("complete");
        }
        
        [Fact]
        public async Task ProcessAsync_WithInvalidInput_ShouldThrow()
        {
            // Arrange & Act
            Func<Task> act = async () => await _classUnderTest.ProcessAsync(null);
            
            // Assert
            await act.Should().ThrowAsync<ArgumentNullException>();
        }
        
        // =====================================================================
        // Helper Methods
        // =====================================================================
        
        private User CreateSampleUser()
        {
            return new User
            {
                Id = 1,
                Username = "testuser",
                Email = "test@example.com",
                CreatedAt = new DateTime(2024, 1, 1, 12, 0, 0)
            };
        }
    }
}
```

## Output Format


```markdown
# Generated Tests for {file_name}

## Summary
- **Test Framework:** pytest/Jest/Go testing
- **Test File:** `tests/{test_file_name}`
- **Coverage Target:** 80%+

## Tests Generated

| Category | Count |
|----------|-------|
| Happy Path | 8 |
| Edge Cases | 12 |
| Error Cases | 6 |
| Integration | 4 |
| **Total** | **30** |

## Test Code

{generated test code}

## Coverage Estimation

Based on the code analyzed, these tests should cover:
- All public methods/functions
- All conditional branches
- All error handling paths

## Recommendations

1. Add integration tests for database operations
2. Consider adding performance benchmarks for hot paths
3. Missing test for {specific scenario}

## To Run Tests

```bash
# Python
pytest tests/test_{module}.py -v --cov={module}

# TypeScript/JavaScript
npm test -- --coverage

# Go
go test -v -cover ./...

# Java (Maven)
mvn test

# Java (Gradle)
./gradlew test --info

# C# (.NET)
dotnet test --collect:"XPlat Code Coverage"
```
```

## Handling Large Files

When generating tests for large modules:

1. **Split by class/function groups**
2. **Prioritize public API**
3. **Use continuation protocol:**

```markdown
## ⚠️ Context Limit Reached

Generated tests for 15/25 functions.

**Completed:**
- ✅ UserService class (8 tests)
- ✅ validate_input function (4 tests)
- ✅ format_output function (3 tests)

**Remaining:**
- ⏳ DatabaseClient class
- ⏳ CacheManager class
- ⏳ Utility functions

**Continue with:**
```
/generate-tests src/services/database.py --continue
```
```

## Arguments

- `$1` - Path to file to generate tests for
- `--framework` - Force framework: `pytest`, `jest`, `vitest`, `go`
- `--coverage` - Target coverage percentage (default: 80)
- `--output` - Output path for test file
- `--continue` - Continue from checkpoint
