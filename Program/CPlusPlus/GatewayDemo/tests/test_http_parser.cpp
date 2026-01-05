#include "../include/http_parser.hpp"
#include "../include/http_types.hpp"
#include <iostream>
#include <cassert>
#include <string>

using namespace gateway;

// 简单的测试框架
int test_count = 0;
int passed_count = 0;

#define TEST(name) \
    void test_##name(); \
    void run_test_##name() { \
        test_count++; \
        std::cout << "Running test: " << #name << "..."; \
        try { \
            test_##name(); \
            passed_count++; \
            std::cout << " PASSED" << std::endl; \
        } catch (const std::exception& e) { \
            std::cout << " FAILED: " << e.what() << std::endl; \
        } \
    } \
    void test_##name()

#define ASSERT_EQ(a, b) \
    if ((a) != (b)) { \
        throw std::runtime_error(std::string("Expected ") + std::to_string(a) + " == " + std::to_string(b)); \
    }

#define ASSERT_STR_EQ(a, b) \
    if ((a) != (b)) { \
        throw std::runtime_error(std::string("Expected '") + (a) + "' == '" + (b) + "'"); \
    }

#define ASSERT_TRUE(cond) \
    if (!(cond)) { \
        throw std::runtime_error("Expected condition to be true"); \
    }

#define ASSERT_FALSE(cond) \
    if (cond) { \
        throw std::runtime_error("Expected condition to be false"); \
    }

// 测试标准HTTP请求解析
TEST(parse_standard_get_request) {
    std::string request_str = 
        "GET /api/users HTTP/1.1\r\n"
        "Host: localhost:8080\r\n"
        "User-Agent: curl/7.68.0\r\n"
        "Accept: */*\r\n"
        "\r\n";
    
    HttpRequest request = HttpParser::parse_request(request_str);
    
    ASSERT_STR_EQ(request.method, "GET");
    ASSERT_STR_EQ(request.path, "/api/users");
    ASSERT_STR_EQ(request.version, "HTTP/1.1");
    ASSERT_STR_EQ(request.headers["Host"], "localhost:8080");
    ASSERT_STR_EQ(request.headers["User-Agent"], "curl/7.68.0");
    ASSERT_STR_EQ(request.headers["Accept"], "*/*");
    ASSERT_TRUE(request.body.empty());
}

TEST(parse_post_request_with_body) {
    std::string request_str = 
        "POST /api/orders HTTP/1.1\r\n"
        "Host: localhost:8080\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 27\r\n"
        "\r\n"
        "{\"order_id\":123,\"item\":\"test\"}";
    
    HttpRequest request = HttpParser::parse_request(request_str);
    
    ASSERT_STR_EQ(request.method, "POST");
    ASSERT_STR_EQ(request.path, "/api/orders");
    ASSERT_STR_EQ(request.version, "HTTP/1.1");
    ASSERT_STR_EQ(request.headers["Content-Type"], "application/json");
    ASSERT_STR_EQ(request.body, "{\"order_id\":123,\"item\":\"test\"}");
}

// 测试边界情况：空头部
TEST(parse_request_with_no_headers) {
    std::string request_str = 
        "GET / HTTP/1.1\r\n"
        "\r\n";
    
    HttpRequest request = HttpParser::parse_request(request_str);
    
    ASSERT_STR_EQ(request.method, "GET");
    ASSERT_STR_EQ(request.path, "/");
    ASSERT_STR_EQ(request.version, "HTTP/1.1");
    ASSERT_TRUE(request.headers.empty());
    ASSERT_TRUE(request.body.empty());
}

// 测试边界情况：大请求体
TEST(parse_request_with_large_body) {
    std::string large_body(10000, 'A');  // 10KB 的数据
    std::string request_str = 
        "POST /api/data HTTP/1.1\r\n"
        "Host: localhost:8080\r\n"
        "Content-Length: " + std::to_string(large_body.size()) + "\r\n"
        "\r\n" + large_body;
    
    HttpRequest request = HttpParser::parse_request(request_str);
    
    ASSERT_STR_EQ(request.method, "POST");
    ASSERT_STR_EQ(request.path, "/api/data");
    ASSERT_EQ(request.body.size(), 10000);
    ASSERT_TRUE(request.body[0] == 'A');
    ASSERT_TRUE(request.body[9999] == 'A');
}

// 测试格式错误的请求：缺少HTTP版本
TEST(parse_malformed_request_no_version) {
    std::string request_str = "GET /api/users\r\n\r\n";
    
    try {
        HttpRequest request = HttpParser::parse_request(request_str);
        throw std::runtime_error("Should have thrown an exception");
    } catch (const std::runtime_error& e) {
        // 预期会抛出异常
        ASSERT_TRUE(true);
    }
}

// 测试格式错误的请求：空请求
TEST(parse_empty_request) {
    std::string request_str = "";
    
    try {
        HttpRequest request = HttpParser::parse_request(request_str);
        throw std::runtime_error("Should have thrown an exception");
    } catch (const std::runtime_error& e) {
        // 预期会抛出异常
        ASSERT_TRUE(true);
    }
}

// 测试HTTP响应解析
TEST(parse_standard_response) {
    std::string response_str = 
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 27\r\n"
        "\r\n"
        "{\"message\":\"Hello World\"}";
    
    HttpResponse response = HttpParser::parse_response(response_str);
    
    ASSERT_EQ(response.status_code, 200);
    ASSERT_STR_EQ(response.status_message, "OK");
    ASSERT_STR_EQ(response.version, "HTTP/1.1");
    ASSERT_STR_EQ(response.headers["Content-Type"], "application/json");
    ASSERT_STR_EQ(response.body, "{\"message\":\"Hello World\"}");
}

// 测试404响应
TEST(parse_404_response) {
    std::string response_str = 
        "HTTP/1.1 404 Not Found\r\n"
        "Content-Length: 0\r\n"
        "\r\n";
    
    HttpResponse response = HttpParser::parse_response(response_str);
    
    ASSERT_EQ(response.status_code, 404);
    ASSERT_STR_EQ(response.status_message, "Not Found");
    ASSERT_TRUE(response.body.empty());
}

// 测试请求序列化
TEST(serialize_request) {
    HttpRequest request;
    request.method = "GET";
    request.path = "/api/users";
    request.version = "HTTP/1.1";
    request.headers["Host"] = "localhost:8080";
    request.headers["Accept"] = "*/*";
    
    std::string serialized = request.to_string();
    
    ASSERT_TRUE(serialized.find("GET /api/users HTTP/1.1") != std::string::npos);
    ASSERT_TRUE(serialized.find("Host: localhost:8080") != std::string::npos);
    ASSERT_TRUE(serialized.find("Accept: */*") != std::string::npos);
}

// 测试响应序列化
TEST(serialize_response) {
    HttpResponse response;
    response.status_code = 200;
    response.status_message = "OK";
    response.version = "HTTP/1.1";
    response.headers["Content-Type"] = "text/plain";
    response.body = "Hello";
    
    std::string serialized = response.to_string();
    
    ASSERT_TRUE(serialized.find("HTTP/1.1 200 OK") != std::string::npos);
    ASSERT_TRUE(serialized.find("Content-Type: text/plain") != std::string::npos);
    ASSERT_TRUE(serialized.find("Hello") != std::string::npos);
}

int main() {
    std::cout << "=== HTTP Parser Unit Tests ===" << std::endl << std::endl;
    
    // 运行所有测试
    run_test_parse_standard_get_request();
    run_test_parse_post_request_with_body();
    run_test_parse_request_with_no_headers();
    run_test_parse_request_with_large_body();
    run_test_parse_malformed_request_no_version();
    run_test_parse_empty_request();
    run_test_parse_standard_response();
    run_test_parse_404_response();
    run_test_serialize_request();
    run_test_serialize_response();
    
    std::cout << std::endl;
    std::cout << "=== Test Summary ===" << std::endl;
    std::cout << "Total tests: " << test_count << std::endl;
    std::cout << "Passed: " << passed_count << std::endl;
    std::cout << "Failed: " << (test_count - passed_count) << std::endl;
    
    return (test_count == passed_count) ? 0 : 1;
}
