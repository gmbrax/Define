# Define
A simple command-line dictionary and thesaurus tool powered by the Merriam-Webster API.

---

## Features
* Fetch definitions from the Merriam-Webster Collegiate Dictionary.
* Find synonyms and antonyms from the Merriam-Webster Collegiate Thesaurus.
* Look up words directly from the command line or via an interactive prompt.
* Filter results to show *only* dictionary or *only* thesaurus entries.

##  Prerequisites
Before you begin, you will need:
* Python 3.11 or higher
* An API Key from Merriam-Webster. You can get your keys [here](https://dictionaryapi.com/).

> **Note:** You will need **separate API keys** for the Collegiate Dictionary and the Collegiate Thesaurus. 
> (Limitations on API usage may apply based on your plan).

## Installation & Setup
Follow these steps to get `Define` up and running.

**1. Clone the repository**


```bash
git clone [https://github.com/your-username/define.git](https://github.com/your-username/define.git)
cd define
```

**2. Create a virtual environment**

This is highly recommended to avoid conflicts with other packages.
```bash 
python3 -m venv .venv
```

**3. Activate the virtual environment**

- On macOS/Linux:
    ```bash
        source .venv/bin/activate
    ```
- On Windows (Command Prompt):
    ```bash
         .venv/Scripts/activate
  ```
**4. Install the Package**

The ```-e``` flag installs the package in "editable" mode, which is useful for development.
```bash
 pip install -e .
```

**5. Configure your API Keys**
Before the first use, you must run the configuration command. You will be prompted to enter the API keys you got in 
the "Prerequisites" step.

```bash
define --configure
```
 Or you can also use:
 ```bash 
 define -c
 ```

## Usage
Once installed and configured, you can run the tool in several ways.

**Interactive Prompt**

Run the command without arguments to be prompted to enter a word. This fetches both dictionary and thesaurus definitions
by default.

```bash
define
```


**Direct Lookup**

Pass a word directly as an argument to skip the prompt.

```bash
define <word>
```

Example:
```bash
define speed
```

**Filtering Results**

You can use flags to get only the results you want. These flags work with both direct lookups and 
the interactive prompt.
- **Dictionary Only**:
   ```bash
    define -d 
    ```

    Example:
    ```bash
    define -d 
    ```
- **Thesaurus Only**:
   ```bash
    define -t 
    ```

    Example:
    ```bash
    define -t 
    ```
  
- **Combining Flags (Example: dictionary only, skipping the prompt)**
    ```bash
    define -d hard
    ```
   