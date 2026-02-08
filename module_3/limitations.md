# System Limitations and Known Issues

This document outlines the current limitations, known issues, and potential improvements for the GradCafe Database Analysis System.

## 🚧 Current Limitations

### 1. Data Format Constraints

#### Format Support
- **Two Formats Only**: System currently supports exactly two JSON formats (old and new). Additional formats require code modifications.
- **Format Detection**: Relies on presence of specific fields (`applicant_status`, `citizenship`, `semester_year_start`) to detect new format. Ambiguous data may be misclassified.
- **Mixed Formats**: Cannot handle JSON files with mixed format records in a single dataset.

#### Date Parsing
- **Limited Date Formats**: Only supports:
  - `DD/MM/YYYY` (e.g., "28/01/2026")
  - `Month DD, YYYY` (e.g., "January 28, 2026")
- **Unsupported Formats**: ISO format (YYYY-MM-DD), Unix timestamps, and other date representations will fail silently (return NULL).
- **Timezone Issues**: No timezone handling; assumes all dates are in same timezone.

#### Numeric Extraction
- **Prefix Dependency**: `extract_numeric()` assumes specific prefixes ("GPA ", "GRE ").
- **Range Values**: Cannot parse ranges (e.g., "GPA 3.5-3.8" or "GRE 320-330").
- **Non-Standard Formats**: Values like "3.5/4.0" or "85%" require manual handling.

### 2. Database Limitations

#### Schema Rigidity
- **Fixed Schema**: Adding new columns requires:
  - Dropping and recreating tables
  - Modifying both `load_data.py` and `data_updater.py`
  - Updating query functions in `query_data.py`
- **No Migration System**: Schema changes require full data reload.

#### Performance
- **No Indexing Strategy**: Only primary key is indexed. Queries on frequently filtered columns (e.g., `status`, `term`, `us_or_international`) are not optimized.
- **Sequential Scans**: Large tables (50,000+ records) may experience slow query times without proper indexes.
- **No Query Optimization**: Queries are not analyzed or optimized for performance.

#### Data Integrity
- **No Foreign Keys**: No referential integrity between potential related tables.
- **No Constraints**: Missing `CHECK` constraints on:
  - `status` (should be enum: Accepted/Rejected/Interview/Wait listed)
  - `us_or_international` (should be American/International)
  - `gpa` (should be 0.0-4.0 or 0.0-5.0)
  - `gre` scores (should be 260-340)
- **Duplicate Detection**: Only checks URL field; programs with multiple applications per URL are not handled.

### 3. Web Scraping Limitations

#### Scraping Constraints
- **Rate Limiting**: No built-in rate limiting beyond page count limit.
- **Error Recovery**: Limited retry logic for network failures.
- **Pagination**: Hardcoded to scrape only 2 pages by default.
- **Anti-Bot Detection**: No handling of CAPTCHAs or anti-scraping measures.
- **Single Source**: Only scrapes from GradCafe; no multi-source support.

#### Background Processing
- **Single Thread**: Only one scraping session can run at a time globally (not per-database).
- **No Queuing**: Multiple scrape requests are rejected rather than queued.
- **Memory Persistence**: Scraping status stored in memory; lost on application restart.
- **No Progress Persistence**: If application crashes during scraping, progress is lost.

### 4. User Interface Limitations

#### Browser Compatibility
- **Modern Browsers Only**: Requires ES6+ JavaScript support.
- **No Fallback**: No graceful degradation for older browsers.
- **Mobile Responsiveness**: Limited testing on mobile devices.

#### Real-Time Updates
- **Polling Based**: Uses 2-second polling for status updates (not WebSocket-based).
- **High Traffic Overhead**: Multiple users cause redundant status checks.
- **No Push Notifications**: Users must keep page open to see scraping completion.

#### Data Visualization
- **Limited Charts**: No graphical visualizations (charts, graphs).
- **Static Tables**: Table in Question 11 has no sorting, filtering, or pagination.
- **No Export**: Cannot export query results to CSV, Excel, or PDF.

### 5. Security Concerns

#### Authentication
- **No User Authentication**: Anyone with network access can use the system.
- **No Authorization**: All users have full access to all features.
- **Session Management**: No session tracking or user-specific settings.

#### Input Validation
- **SQL Injection**: Query functions are safe (use parameterized queries), but no validation on database switching parameter.
- **XSS Vulnerabilities**: User input from scraping not sanitized for HTML display.
- **No Input Sanitization**: Database name parameter in API endpoints not strictly validated.

#### Data Protection
- **No Encryption**: Data transmitted in plain HTTP (no HTTPS).
- **Credentials**: Database credentials hardcoded in source files.
- **No Backup Strategy**: No automated database backups.

### 6. Error Handling

#### Robustness
- **Generic Error Messages**: Database errors shown to users may expose system details.
- **Silent Failures**: Some errors (e.g., date parsing) fail silently without logging.
- **No Logging System**: No application logs for debugging production issues.
- **Limited Validation**: Missing validation for:
  - Empty database result sets
  - Malformed JSON in scraped data
  - Corrupted database state

#### Recovery
- **No Rollback Mechanism**: Failed batch inserts may leave database in inconsistent state.
- **No Data Validation**: Invalid data can be inserted into database.
- **No Health Checks**: No endpoint to verify system health or database connectivity.

### 7. Scalability Issues

#### Data Volume
- **Memory Loading**: Entire JSON file loaded into memory before processing.
- **Batch Size**: No configurable batch size for inserts.
- **Large Files**: Files over 500MB may cause memory issues.

#### Concurrent Users
- **Single-Threaded Flask**: Development server not designed for production.
- **No Load Balancing**: Single instance handles all requests.
- **Resource Contention**: Multiple users scraping simultaneously may cause issues.

#### Database Connections
- **No Connection Pooling**: New connection for every query.
- **No Connection Limits**: Unlimited concurrent connections may exhaust PostgreSQL resources.

### 8. Code Maintenance

#### Documentation
- **Inline Comments**: Limited inline code documentation.
- **API Documentation**: No OpenAPI/Swagger documentation.
- **Architecture Docs**: No system architecture diagrams.

#### Testing
- **No Unit Tests**: No automated test suite.
- **No Integration Tests**: Database queries not tested automatically.
- **Manual Testing Only**: All testing done manually through web interface.

#### Code Quality
- **No Type Hints**: Python code lacks type annotations.
- **Magic Numbers**: Hardcoded values (e.g., 2 pages, 2-second polling).
- **Duplicate Code**: Similar logic in `load_data.py` and `data_updater.py`.

## 🔄 Potential Improvements

### High Priority

1. **Add Database Indexes**
   ```sql
   CREATE INDEX idx_status ON gradcafe_main(status);
   CREATE INDEX idx_term ON gradcafe_main(term);
   CREATE INDEX idx_url ON gradcafe_main(url);
   ```

2. **Implement Connection Pooling**
   - Use `psycopg2.pool` for connection management
   - Configure min/max connection limits

3. **Add Input Validation**
   - Validate `dbname` parameter against whitelist
   - Sanitize user inputs before database operations

4. **Implement Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

5. **Add Error Handling**
   - Try-catch blocks with specific exception handling
   - User-friendly error messages
   - Log detailed errors for debugging

### Medium Priority

6. **Unit Testing**
   - Test format detection logic
   - Test date parsing functions
   - Test query functions with mock data

7. **Configuration Management**
   - Move credentials to environment variables
   - Use config files for settings
   - Support multiple environments (dev/prod)

8. **Data Validation**
   - Add constraints to database schema
   - Validate data before insertion
   - Implement data quality checks

9. **Performance Optimization**
   - Batch inserts for large datasets
   - Streaming JSON parser for large files
   - Query optimization and analysis

10. **Enhanced UI**
    - Add data visualization charts
    - Implement table sorting/filtering
    - Add CSV export functionality

### Low Priority

11. **Multi-Database Support**
    - Support MySQL, SQLite
    - Abstract database layer
    - Database-agnostic queries

12. **Advanced Scraping**
    - Configurable scraping parameters
    - Multi-source scraping
    - Intelligent rate limiting

13. **User Management**
    - Authentication system
    - User roles and permissions
    - Personal dashboards

14. **Real-Time Updates**
    - WebSocket integration
    - Live query results
    - Push notifications

15. **Advanced Analytics**
    - Machine learning predictions
    - Trend analysis
    - Comparative analytics

## 📊 Known Bugs

### Critical
- None currently identified

### Major
- **Empty Database Query Results**: Queries on empty databases return "N/A" but may cause UI display issues in some browsers.
- **Concurrent Scraping**: Multiple simultaneous scrape requests may cause race conditions in status updates.

### Minor
- **Long Program Names**: Overflow in UI cards for very long program names.
- **Special Characters**: Some Unicode characters in comments may not display correctly.
- **Browser Back Button**: Using browser back/forward may show stale data until page refresh.

## 🔮 Future Considerations

### Feature Requests
- **Advanced Filtering**: Filter results by university, program, GPA range, etc.
- **Comparison Tool**: Compare statistics between different universities/programs
- **Trend Analysis**: Historical data comparison across years
- **Email Notifications**: Alert users when new data matching criteria is added
- **API Access**: RESTful API for programmatic access to data

### Technical Debt
- Refactor duplicate code between `load_data.py` and `data_updater.py`
- Extract configuration into separate files
- Implement proper ORM (SQLAlchemy) instead of raw SQL
- Migrate to production WSGI server (Gunicorn/uWSGI)
- Add Docker containerization for easier deployment

## 📞 Reporting Issues

When reporting issues, please include:
1. Python version
2. PostgreSQL version
3. Operating system
4. Steps to reproduce
5. Expected vs actual behavior
6. Error messages (if any)
7. Browser console errors (for UI issues)

---

**Note**: This system is designed for educational purposes and is not production-ready without addressing the limitations listed above.

**Last Updated**: February 8, 2026  
**Version**: 1.0  
**Maintainer**: Course Project Team
