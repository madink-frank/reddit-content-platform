# Admin Dashboard User Guide

## Overview

The Reddit Content Platform Admin Dashboard is a comprehensive web application for managing your content crawling, trend analysis, and blog generation operations. This guide will help you navigate and use all features effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Dashboard Overview](#dashboard-overview)
4. [Keyword Management](#keyword-management)
5. [Crawling Operations](#crawling-operations)
6. [Posts Management](#posts-management)
7. [Trend Analysis](#trend-analysis)
8. [Content Generation](#content-generation)
9. [System Monitoring](#system-monitoring)
10. [Settings](#settings)
11. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements

- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Screen Resolution**: Minimum 1024x768 (optimized for 1920x1080)
- **Internet Connection**: Stable connection required for real-time features

### Accessing the Dashboard

1. **URL**: Navigate to your dashboard URL (e.g., `https://admin.yourplatform.com`)
2. **Login**: Click "Login with Reddit" to authenticate
3. **Authorization**: Grant necessary permissions to the application
4. **Dashboard**: You'll be redirected to the main dashboard

## Authentication

### Initial Login

1. **Click "Login with Reddit"**
   - You'll be redirected to Reddit's OAuth2 page
   - Grant the requested permissions
   - You'll be redirected back to the dashboard

2. **Token Management**
   - Access tokens are automatically managed
   - Refresh tokens are used for seamless re-authentication
   - Sessions expire after 7 days of inactivity

### Logout

- Click your profile icon in the top-right corner
- Select "Logout" from the dropdown menu
- You'll be redirected to the login page

## Dashboard Overview

### Main Navigation

The dashboard uses a sidebar navigation with the following sections:

- **🏠 Dashboard**: Overview and quick stats
- **🔑 Keywords**: Manage your tracked keywords
- **🕷️ Crawling**: Control crawling operations
- **📄 Posts**: View and manage collected posts
- **📊 Analytics**: Trend analysis and insights
- **✍️ Content**: Generated blog content management
- **🖥️ System**: System monitoring and health
- **⚙️ Settings**: User preferences and configuration

### Dashboard Widgets

The main dashboard displays:

1. **System Status**: Overall health indicators
2. **Recent Activity**: Latest crawling and generation activities
3. **Quick Stats**: Key metrics at a glance
4. **Active Keywords**: Currently tracked keywords
5. **Recent Posts**: Latest collected Reddit posts
6. **Trend Highlights**: Top trending topics

## Keyword Management

### Adding Keywords

1. **Navigate to Keywords** section
2. **Click "Add Keyword"** button
3. **Fill in the form**:
   - **Keyword**: The term to track (e.g., "artificial intelligence")
   - **Description**: Optional description for organization
   - **Active**: Toggle to enable/disable tracking
4. **Click "Save"** to add the keyword

### Managing Keywords

#### Viewing Keywords
- All keywords are displayed in a searchable table
- Use the search bar to find specific keywords
- Filter by status (Active/Inactive)

#### Editing Keywords
1. **Click the edit icon** (✏️) next to a keyword
2. **Modify the details** in the popup form
3. **Click "Update"** to save changes

#### Deleting Keywords
1. **Click the delete icon** (🗑️) next to a keyword
2. **Confirm deletion** in the popup dialog
3. **Note**: This will also delete all associated posts and data

### Keyword Status

- **🟢 Active**: Keyword is being tracked and crawled
- **🔴 Inactive**: Keyword is paused (no new crawling)
- **⚠️ Error**: Issues with the keyword (check logs)

## Crawling Operations

### Starting Crawling

1. **Navigate to Crawling** section
2. **Select Keywords**: Choose which keywords to crawl
3. **Configure Settings**:
   - **Limit**: Number of posts to collect (default: 50)
   - **Time Filter**: Time range (hour, day, week, month, year, all)
   - **Sort Method**: How to sort results (hot, new, top, rising)
4. **Click "Start Crawling"**

### Monitoring Crawling

#### Real-time Status
- **Progress Bar**: Shows crawling completion percentage
- **Status Indicators**: 
  - 🟡 Pending: Waiting to start
  - 🔵 Running: Currently crawling
  - 🟢 Completed: Successfully finished
  - 🔴 Failed: Encountered errors

#### Crawling History
- View past crawling operations
- Filter by date range, keyword, or status
- Click on any entry to see detailed logs

### Stopping Crawling

1. **Find the running task** in the active crawling section
2. **Click "Stop"** button
3. **Confirm** in the popup dialog
4. The task will be marked as cancelled

## Posts Management

### Viewing Posts

#### Post List
- All collected posts are displayed in a paginated table
- **Columns**: Title, Subreddit, Score, Comments, Date
- **Sorting**: Click column headers to sort
- **Filtering**: Use filters to narrow down results

#### Post Details
1. **Click on a post title** to view full details
2. **Modal displays**:
   - Full post content
   - Comments (if collected)
   - Metadata (author, score, URL)
   - Associated keyword

### Filtering Posts

Use the filter panel to narrow down posts:

- **Keywords**: Filter by associated keywords
- **Subreddits**: Filter by specific subreddits
- **Date Range**: Select start and end dates
- **Score Range**: Filter by Reddit score
- **Comment Count**: Filter by number of comments

### Searching Posts

1. **Use the search bar** at the top of the posts section
2. **Search in**:
   - Post titles
   - Post content
   - Author names
   - Subreddit names
3. **Results update** in real-time as you type

### Managing Posts

#### Deleting Posts
1. **Select posts** using checkboxes
2. **Click "Delete Selected"** button
3. **Confirm deletion** in the popup dialog

#### Exporting Posts
1. **Select posts** or use "Select All"
2. **Click "Export"** button
3. **Choose format**: CSV, JSON, or Excel
4. **Download** will start automatically

## Trend Analysis

### Viewing Trends

#### Trend Dashboard
- **Keyword Trends**: Line charts showing keyword popularity over time
- **TF-IDF Scores**: Importance scores for different terms
- **Engagement Metrics**: Upvotes, comments, and interaction rates
- **Trend Velocity**: How quickly topics are gaining/losing popularity

#### Trend Comparison
1. **Select multiple keywords** from the dropdown
2. **Choose time range** for comparison
3. **View comparative charts** showing relative performance
4. **Export data** for further analysis

### Generating Trend Reports

1. **Navigate to Analytics** section
2. **Click "Generate Report"**
3. **Configure report**:
   - **Keywords**: Select which keywords to include
   - **Time Range**: Choose analysis period
   - **Metrics**: Select which metrics to include
4. **Click "Generate"** and wait for processing
5. **Download** the generated report

### Understanding Metrics

- **TF-IDF Score**: Term frequency-inverse document frequency (higher = more important)
- **Engagement Score**: Combined metric of upvotes, comments, and shares
- **Trend Velocity**: Rate of change in popularity (positive = growing, negative = declining)
- **Sentiment Score**: Overall sentiment of discussions (if enabled)

## Content Generation

### Generating Blog Posts

1. **Navigate to Content** section
2. **Click "Generate New Content"**
3. **Configure generation**:
   - **Keywords**: Select source keywords for content
   - **Template**: Choose blog post template (default, listicle, news)
   - **Length**: Target word count
   - **Tone**: Professional, casual, or technical
4. **Click "Generate"** and wait for processing

### Managing Generated Content

#### Content List
- View all generated blog posts
- **Status indicators**:
  - 📝 Draft: Generated but not published
  - ✅ Published: Live on blog site
  - ❌ Rejected: Marked as not suitable

#### Editing Content
1. **Click on a content title** to open the editor
2. **Use the markdown editor** to make changes
3. **Preview** changes in real-time
4. **Save** or **Publish** when ready

#### Publishing Content
1. **Select content** from the list
2. **Click "Publish"** button
3. **Configure publishing**:
   - **Publish Date**: Schedule for future or publish immediately
   - **Categories**: Assign to blog categories
   - **Tags**: Add relevant tags
   - **Featured Image**: Upload or select image
4. **Confirm publishing**

### Content Templates

#### Available Templates
- **Default**: Standard blog post format
- **Listicle**: Numbered or bulleted list format
- **News**: News article format with lead paragraph
- **Tutorial**: Step-by-step guide format
- **Review**: Product or service review format

#### Customizing Templates
1. **Navigate to Settings** > **Content Templates**
2. **Select a template** to edit
3. **Modify the template** using markdown and variables
4. **Save changes** to apply to future generations

## System Monitoring

### Health Dashboard

#### System Status
- **API Status**: Backend API health
- **Database**: Database connection and performance
- **Redis**: Cache and session storage status
- **Celery**: Background task processing status
- **External APIs**: Reddit API and other integrations

#### Performance Metrics
- **Response Times**: API endpoint performance
- **Error Rates**: System error frequency
- **Resource Usage**: CPU, memory, and disk usage
- **Active Users**: Current dashboard users

### Alerts and Notifications

#### Alert Types
- 🔴 **Critical**: System down or major issues
- 🟡 **Warning**: Performance degradation or minor issues
- 🔵 **Info**: General system information
- 🟢 **Success**: Successful operations

#### Managing Alerts
1. **View alerts** in the notifications panel
2. **Click on an alert** to see details
3. **Acknowledge** alerts to mark as seen
4. **Configure alert preferences** in Settings

### Logs and Debugging

#### Viewing Logs
1. **Navigate to System** > **Logs**
2. **Filter logs** by:
   - **Level**: Error, Warning, Info, Debug
   - **Component**: API, Crawler, Generator, etc.
   - **Time Range**: Last hour, day, week
3. **Search logs** using keywords

#### Downloading Logs
1. **Configure filters** for the logs you need
2. **Click "Export Logs"**
3. **Choose format**: Text or JSON
4. **Download** will start automatically

## Settings

### User Profile

#### Profile Information
- **Name**: Display name in the dashboard
- **Email**: Contact email (from Reddit OAuth)
- **Avatar**: Profile picture (from Reddit)
- **Timezone**: For displaying dates and times

#### Preferences
- **Theme**: Light or dark mode
- **Language**: Interface language (if multiple supported)
- **Notifications**: Email and in-app notification preferences
- **Dashboard Layout**: Customize widget arrangement

### System Configuration

#### API Settings
- **Rate Limits**: Configure API rate limiting
- **Timeout Settings**: Request timeout configurations
- **Retry Policies**: Automatic retry configurations

#### Crawling Settings
- **Default Limits**: Default number of posts to crawl
- **Scheduling**: Automatic crawling schedules
- **Filters**: Global content filters

#### Content Generation Settings
- **Default Templates**: Set preferred templates
- **AI Settings**: Configure content generation parameters
- **Publishing**: Default publishing settings

### Account Management

#### Connected Accounts
- **Reddit Account**: View connected Reddit account details
- **API Keys**: Manage API keys for external services
- **Webhooks**: Configure webhook endpoints

#### Security
- **Active Sessions**: View and manage active login sessions
- **API Tokens**: Generate and manage API access tokens
- **Two-Factor Authentication**: Enable 2FA (if supported)

## Troubleshooting

### Common Issues

#### Login Problems
**Issue**: Can't log in or getting authentication errors
**Solutions**:
1. Clear browser cache and cookies
2. Try incognito/private browsing mode
3. Check if Reddit is accessible
4. Contact support if issues persist

#### Crawling Not Working
**Issue**: Crawling tasks fail or don't start
**Solutions**:
1. Check keyword validity (no special characters)
2. Verify Reddit API status
3. Check system status in monitoring section
4. Try reducing crawling limits

#### Content Generation Fails
**Issue**: Blog post generation doesn't work
**Solutions**:
1. Ensure you have collected posts for the keywords
2. Check if trend analysis has been run
3. Verify template settings
4. Check system logs for errors

#### Dashboard Loading Issues
**Issue**: Dashboard is slow or doesn't load
**Solutions**:
1. Check internet connection
2. Try refreshing the page
3. Clear browser cache
4. Try a different browser
5. Check system status

### Performance Optimization

#### Browser Performance
- **Close unused tabs** to free up memory
- **Use latest browser version** for best performance
- **Disable unnecessary extensions** that might interfere
- **Clear cache regularly** to prevent slowdowns

#### Dashboard Usage
- **Use filters** to reduce data loading
- **Limit date ranges** when viewing large datasets
- **Close modals and popups** when not needed
- **Refresh page** if it becomes unresponsive

### Getting Help

#### Support Channels
- **Documentation**: Check this guide and API docs
- **System Logs**: Check logs for error details
- **GitHub Issues**: Report bugs and request features
- **Email Support**: Contact support team

#### Reporting Issues
When reporting issues, include:
1. **Browser and version**
2. **Steps to reproduce**
3. **Error messages** (if any)
4. **Screenshots** (if helpful)
5. **System logs** (if relevant)

## Best Practices

### Keyword Management
- Use specific, relevant keywords
- Regularly review and update keyword lists
- Remove inactive or irrelevant keywords
- Monitor keyword performance

### Crawling Strategy
- Start with smaller limits to test
- Use appropriate time filters for your needs
- Schedule crawling during off-peak hours
- Monitor crawling success rates

### Content Generation
- Ensure sufficient data before generating content
- Review generated content before publishing
- Customize templates for your brand voice
- Use appropriate categories and tags

### System Maintenance
- Regularly check system health
- Monitor resource usage
- Keep track of API rate limits
- Review and acknowledge alerts promptly

## Keyboard Shortcuts

### Global Shortcuts
- `Ctrl/Cmd + K`: Open search
- `Ctrl/Cmd + /`: Show keyboard shortcuts
- `Esc`: Close modals and popups
- `Ctrl/Cmd + R`: Refresh current view

### Navigation Shortcuts
- `G + D`: Go to Dashboard
- `G + K`: Go to Keywords
- `G + C`: Go to Crawling
- `G + P`: Go to Posts
- `G + A`: Go to Analytics
- `G + T`: Go to Content
- `G + S`: Go to System
- `G + E`: Go to Settings

### Action Shortcuts
- `N`: Create new (context-dependent)
- `E`: Edit selected item
- `Del`: Delete selected item
- `Ctrl/Cmd + S`: Save current form
- `Ctrl/Cmd + Enter`: Submit current form

---

**Version**: 1.0.0  
**Last Updated**: 2025-08-03  
**Support**: For additional help, contact our support team or check the system documentation.