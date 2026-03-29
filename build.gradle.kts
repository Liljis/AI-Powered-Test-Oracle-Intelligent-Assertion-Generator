plugins {
    kotlin("jvm") version "1.9.22"
    application
}

group = "com.testoracle"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin
    implementation(kotlin("stdlib"))
    implementation("org.jetbrains.kotlin:kotlin-reflect:1.9.22")
    
    // JSON Processing (for Bob AI)
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Logging
    implementation("org.slf4j:slf4j-api:2.0.9")
    implementation("ch.qos.logback:logback-classic:1.4.14")
    
    // Testing
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.10.1")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.10.1")
    
    // AssertJ for fluent assertions
    testImplementation("org.assertj:assertj-core:3.24.2")
}

tasks.test {
    useJUnitPlatform()
    
    // Enable parallel test execution
    maxParallelForks = Runtime.getRuntime().availableProcessors()
    
    // Set test logging
    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = false
        showExceptions = true
        showCauses = true
        showStackTraces = true
    }
    
    // Set environment variables for tests
    environment("WATSONX_API_KEY", System.getenv("WATSONX_API_KEY") ?: "")
    environment("WATSONX_URL", System.getenv("WATSONX_URL") ?: "https://us-south.ml.cloud.ibm.com")
    environment("WATSONX_PROJECT_ID", System.getenv("WATSONX_PROJECT_ID") ?: "")
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        jvmTarget = "11"
        freeCompilerArgs = listOf("-Xjsr305=strict")
    }
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

application {
    mainClass.set("com.testoracle.examples.BobAIExampleKt")
}

// Task to run the Bob AI example (no credentials needed!)
tasks.register("runBobAI") {
    group = "application"
    description = "Run the Bob AI example (no credentials required)"
    dependsOn("classes")
    doLast {
        javaexec {
            mainClass.set("com.testoracle.examples.BobAIExampleKt")
            classpath = sourceSets["main"].runtimeClasspath
        }
    }
}