#!/bin/bash
# Scaffold a Selenium + Java project with Maven
set -e

PROJECT_NAME="${1:-selenium-project}"
CLOUD="${2:-}"

if [ -d "$PROJECT_NAME" ]; then
    echo "Error: Directory '$PROJECT_NAME' already exists"
    exit 2
fi

command -v mvn >/dev/null 2>&1 || { echo "Error: Maven (mvn) not found"; exit 1; }

echo "Creating Selenium project: $PROJECT_NAME"
mkdir -p "$PROJECT_NAME/src/main/java/pages"
mkdir -p "$PROJECT_NAME/src/test/java/tests"
mkdir -p "$PROJECT_NAME/src/test/resources"

cat > "$PROJECT_NAME/pom.xml" << 'POMEOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>selenium-tests</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <selenium.version>4.27.0</selenium.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.seleniumhq.selenium</groupId>
            <artifactId>selenium-java</artifactId>
            <version>${selenium.version}</version>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.11.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
POMEOF

echo "✅ Project '$PROJECT_NAME' created"
echo "   cd $PROJECT_NAME && mvn test"
exit 0
