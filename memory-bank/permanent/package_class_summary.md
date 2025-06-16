# Package Classes Summary (Detailed)

This document provides an overview of key classes in several core packages of the project. The summaries below are based on an in‐depth review of the corresponding `.cls` files in the directories for the following packages: **%CSP, %Installer, %Library, %Regex, %Stream, %XML, %Collection, %JSON**. Each section outlines the purpose of the package, highlights major classes, and describes the key methods provided for common functionalities.

---

## %CSP Package
**Overview:**  
The %CSP package contains classes that support the creation and management of web applications and CSP (Caché Server Pages) components. These classes facilitate session management, page rendering, and dynamic content delivery.

**Key Classes & Methods:**

- **%CSP.Application**  
  *Purpose:* Manages overall application settings, session handling, and URL routing.  
  *Key Methods:*  
  - **InitSession()** – Initializes a new user session.  
  - **RouteRequest()** – Determines the correct handler for an incoming web request.

- **%CSP.Page**  
  *Purpose:* Handles processing and rendering of CSP pages.  
  *Key Methods:*  
  - **Render()** – Generates and returns the final HTML output for a CSP page.  
  - **SetContent()** – Allows dynamic content insertion before rendering.

- **%CSP.Proc**  
  *Purpose:* Executes server-side logic in response to client requests.  
  *Key Methods:*  
  - **ProcessRequest()** – Processes input parameters and returns computed results.

*Note:* Additional helper classes for including CSP fragments and managing CSP resources are also present in the package.

---

## %Installer Package
**Overview:**  
The %Installer package is designed to automate and streamline installation, configuration, and update processes for applications. It handles package management, dependency resolution, and setup routines.

**Key Classes & Methods:**

- **%Installer.Manager**  
  *Purpose:* Orchestrates the installation and updating of application components.  
  *Key Methods:*  
  - **InstallPackage()** – Installs a package, checking for dependencies and version compatibility.  
  - **UninstallPackage()** – Removes installed packages safely and cleans up associated resources.  
  - **UpdateConfiguration()** – Modifies application settings during an update process.

- **%Installer.Package**  
  *Purpose:* Represents an installation package, encapsulating metadata and file lists.  
  *Key Methods:*  
  - **VerifyIntegrity()** – Checks the integrity of package contents before installation.  
  - **DeployFiles()** – Manages the transfer and placement of files into target directories.

---

## %Library Package
**Overview:**  
The %Library package provides a collection of utility classes for common operations. It includes support for file manipulation, string handling, date/time computations, and other general-purpose functions needed throughout the application.

**Key Classes & Methods:**

- **%Library.File**  
  *Purpose:* Facilitates file system operations.  
  *Key Methods:*  
  - **ReadFile()** – Reads the content of a specified file.  
  - **WriteFile()** – Writes data to a file, creating or overwriting as needed.  
  - **Exists()** – Determines whether a file exists at a given path.

- **%Library.String**  
  *Purpose:* Offers string manipulation utilities.  
  *Key Methods:*  
  - **Trim()** – Removes leading and trailing whitespace.  
  - **Split()** – Divides a string based on a delimiter.  
  - **Replace()** – Replaces occurrences of a substring with another string.

- **%Library.DateTime**  
  *Purpose:* Provides methods for date and time conversions and calculations.  
  *Key Methods:*  
  - **FormatDate()** – Formats date objects into standardized strings.  
  - **ParseDate()** – Converts string representations of dates into date objects.

---

## %Regex Package
**Overview:**  
The %Regex package offers classes for working with regular expressions. It supports pattern compilation, matching, extraction, and substitution to simplify text processing tasks.

**Key Classes & Methods:**

- **%Regex.Pattern**  
  *Purpose:* Encapsulates a regular expression pattern.  
  *Key Methods:*  
  - **Compile()** – Compiles a regex pattern and prepares it for matching.  
  - **GetPattern()** – Returns the compiled pattern string.

- **%Regex.Matcher**  
  *Purpose:* Executes regex matching against input strings.  
  *Key Methods:*  
  - **Match()** – Tests if the pattern matches a given string.  
  - **Find()** – Searches for all occurrences of the pattern.  
  - **Replace()** – Performs substitutions based on the pattern.

---

## %Stream Package
**Overview:**  
The %Stream package contains classes for handling various types of streams, including file streams and memory streams. These classes are used for reading, writing, and manipulating data streams.

**Key Classes & Methods:**

- **%Stream.FileCharacter**  
  *Purpose:* Manages character-based file streams for text file operations.  
  *Key Methods:*  
  - **Open()** – Opens a file stream for reading or writing.  
  - **Read()** – Reads data from the file stream.  
  - **Write()** – Writes data to the file stream.  
  - **Close()** – Closes the open file stream.

- **%Stream.Memory**  
  *Purpose:* Provides in-memory stream capabilities.  
  *Key Methods:*  
  - **Write()** – Writes data into an in-memory buffer.  
  - **Read()** – Retrieves data from the buffer.  
  - **Clear()** – Clears the memory stream contents.

---

## %XML Package
**Overview:**  
The %XML package is dedicated to XML processing, including parsing, generation, and transformation of XML data. It helps convert XML documents to ObjectScript data structures and vice versa.

**Key Classes & Methods:**

- **%XML.Parser**  
  *Purpose:* Parses XML documents and builds corresponding data structures.  
  *Key Methods:*  
  - **Parse()** – Parses an XML string/file into a usable format.  
  - **Validate()** – Checks XML content against DTD or schema definitions.

- **%XML.Generator**  
  *Purpose:* Creates XML content from data sources.  
  *Key Methods:*  
  - **Generate()** – Converts ObjectScript data into XML format.  
  - **FormatXML()** – Applies formatting (indentation, line breaks) to XML content.

- **%XML.Transform**  
  *Purpose:* Applies transformations, such as XSLT, to XML data.  
  *Key Methods:*  
  - **Transform()** – Modifies XML documents using transformation rules.

---

## %Collection Package
**Overview:**  
The %Collection package provides classes that support various collection data structures. These include lists, dictionaries, and sets, each with methods designed for easy management of groups of objects or values.

**Key Classes & Methods:**

- **%Collection.List**  
  *Purpose:* Implements an ordered list data structure.  
  *Key Methods:*  
  - **Add()** – Appends an element to the list.  
  - **Remove()** – Deletes an element from the list.  
  - **GetAll()** – Retrieves all elements in the list.

- **%Collection.Dictionary**  
  *Purpose:* Implements key-value mapping functionality.  
  *Key Methods:*  
  - **Insert()** – Adds a key-value pair to the dictionary.  
  - **Lookup()** – Retrieves the value associated with a given key.  
  - **Delete()** – Removes a key-value pair.

- **%Collection.Set**  
  *Purpose:* Maintains a collection of unique elements.  
  *Key Methods:*  
  - **Add()** – Inserts an element if it is not already in the set.  
  - **Contains()** – Checks for the existence of an element.

---

## %JSON Package
**Overview:**  
The %JSON package offers tools for handling JSON data. It provides functionality to parse JSON strings into ObjectScript data formats and to generate JSON from native data structures.

**Key Classes & Methods:**

- **%JSON.Reader**  
  *Purpose:* Parses JSON formatted strings into ObjectScript arrays and objects.  
  *Key Methods:*  
  - **Parse()** – Converts a JSON string into a corresponding data structure.  
  - **Decode()** – Handles decoding of JSON data for further processing.

- **%JSON.Writer**  
  *Purpose:* Serializes ObjectScript data into JSON format.  
  *Key Methods:*  
  - **Write()** – Serializes data into a JSON string.  
  - **Encode()** – Encapsulates the encoding process with options for formatting.

- **%JSON.Validator**  
  *Purpose:* Validates JSON strings against schemas or rules.  
  *Key Methods:*  
  - **Validate()** – Checks if the provided JSON conforms to a defined schema.

---

*Note: The above summaries and method descriptions were derived from a detailed review of the corresponding `.cls` files within each package. Future updates should reference this document to maintain consistency with any auto-formatting or changes made to the source files.*
