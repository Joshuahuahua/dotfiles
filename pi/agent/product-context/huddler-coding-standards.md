<!--
  Source: Huddler wiki, "Infrastructure-(Internal)/Coding-Standards-+-Guiding-Principals.md"
  Synced from wiki commit: 81f1ff8d5d9bdf0040add87aa90d7d5219ddaf4c (2026-05-19 07:49:26 +0000)
  Do not edit by hand — refresh via the "wiki-sync" skill instead.

  This file is symlinked as AGENTS.md into the Huddler product repo working
  copies (workspace1/2/3) so it's automatically applied as project context
  any time work happens in that repo.
-->

[[_TOC_]]

## Background

Development in a consultancy context is often affected largely by:

- Time and budget constraints
- Resourcing constraints
- Requirement changes late in the delivery cycle

This usually leads to an accumulation of technical debt in software solutions where the primary focus is on delivering functionality rather than code quality.

Within reason, team members should aim to make progressive improvements to the code base. If a critical issue is identified, it should be highlighted and if possible, addressed. 

However, a balance needs to be struck between progressive improvements and larger scale refactoring considering delivery timelines.

Immediate concerns that the team should aim to progressively address are:

- Naming convention application within the work scope
- Refactoring within targeted functions: breaking down large functions, react components, API optimised queries, error handling and SASS improvements
- Package level improvements in relation to SPFx applications
- Identified critical errors.


## Instructions
- This Wiki contains the agreed-upon coding standards that all pull-requests submitted will be held to.
- With the team, please discuss any coding standards/practices you would like the team to adopt before adding them to this page.
- Do **NOT** remove anything from this wiki unless discussed with the team first.
- The coding standards should be viewed as an active wiki. They should be reviewed regularly to ensure the information is relevant and applicable to the team's composition and way of working. The standards should cater for any changes in development frameworks and tools.

## Guiding Principals

---

### When checking permissions, check *permissions*.
Rather than using the logic of "if the user is in the member group, they will have edit permissions for [some] resource", actually check that permission for that user explicitly. 

## Standards

---

### Type-safe
To be type-safe in code is to ensure that values are only used according to their defined types, preventing invalid operations and reducing runtime errors.

**Ensure you:**
- [ ] Define clear types for variables, functions, and objects.
- [ ] Avoid using `any` where possible
- [ ] Validate external inputs and outputs e.g. API's

---

### TypeScript Naming Conventions

| Component                              | Description                                                        | Convention                               | Example              |
|----------------------------------------|--------------------------------------------------------------------|------------------------------------------|----------------------|
| Constants                              | For values re-used across multiple functions                       | Upper case separated by underscores      | CONTENT_TYPE_ID      |
| Variables and function-level constants |                                                                    | camelCase                                | dueDate              |
| Functions                              |                                                                    | camelCase                                | dueDate              |
| Interface                              | The preference is to use types in place of Interface declarations  | PascalCase                               | NewsArticle          |
| Types                                  |                                                                    | PascalCase                               | NewsArticle          |
| Enum                                   | Only use an enum if the associated value is not clear (obfuscated) | PascalCase                               | ViewTypes            |
| Enum members                           |                                                                    | PascalCase                               | ViewTypes.SlideShow  |
| Boolean variables                      |                                                                    | camelCase and prefix with "is" or "has". | isValid or hasValues |

---

### Recommended Conventions

> A lot of the following concepts can be found here: [https://developer.mozilla.org/en-US/](https://developer.mozilla.org/en-US/) 

- Use `let` and `const` instead of the ambiguous `var`
- Use `undefined` over `null` to indicate the absence of a value
- Use `types` over `interfaces`
- Pass only the required properties to child components
- Let the LSP infer return types for functions
- Descriptive function names
- Regular Expressions (RegEx)
- String Interpolation
- Ternary Expressions
- Unary Operators
- Logical Assignment
- Spread Syntax
- Optional Chaining

---

### Code Comments

Comments allow for code-level documentation providing an overview of a function's purpose and parameters. Properly written comments can be surfaced by IntelliSense tools. A balanced approach should be taken with code comments. Not every function or line of code needs to be commented on.

When working with functions, please use JSDoc style comments.

```
/**
 * Adds two numbers together.
 * @param {number} a - The first number.
 * @param {number} b - The second number.
 * @returns {number} The sum of a and b.
*/
function add(a, b) {
 return a + b;
}
```
Aim to write comments for:

- High-level functions
- Complex functions or logic (where the implementation's purpose may not be obvious) e.g. Regex expressions
- A piece of code where a non-typical requirement needs to be met.

---

### General PR Standards

- The person who raised/created the comment must close it. If they are unable too, the comment will be delegated to a 3rd party and they will review the comment and associated context to then close off the comment if neccessary.
- DO NOT make changes using the Azure Devops PR UI. Always make the changes on your code editor and push those changes as a new commit or amended with the previous commit.

---

### Conventional Commit Messages

Please ensure, when creating your commit message, you follow the [Conventional Commit Specifications](https://www.conventionalcommits.org/en/v1.0.0/).

Doing this will:
- Provide a clear, consistent structure for commit messages
- Make commit history easy to read and understand
- Enables changelog generation
- Helps identify the purpose of changes (fix, feat, etc.)

#### List of Commit Prefixes
| Type     | Description                                                                                           |
|----------|-------------------------------------------------------------------------------------------------------|
| build    | Changes that affect the build system or external dependencies (example scopes: pnpm, npm)             |
| chore    | Maintenance tasks and other changes that do not modify source code or test files (dependency updates) |
| ci       | Changes to CI/CD configuration files and scripts                                                      |
| docs     | Documentation-only changes                                                                            |
| feat     | A new feature                                                                                         |
| fix      | A bug fix                                                                                             |
| refactor | A code change that neither fixes a bug nor adds a feature                                             |
| revert   | A previous change is being undone                                                                     |
| style    | Changes that affect the look of a feature without changing its business logic                         |
| test     | Adding, editing, or removing tests                                                                    |

#### List of Commit Scopes:
| Scope               | Description                                                      |
|---------------------|------------------------------------------------------------------|
| igloo               | Anything Igloo-related                                           |
| analytics           | Anything Analytics-related                                       |
| dochq               | Anything DocHq-related                                           |
| hub                 | Something that applies either *generally* to hub or to all of it |
| nav                 | Something related to Hub Navigation                              |
| pagewizard          | Anything Page Wizard-related                                     |
| studio              | Anything Huddler Studio-related                                  |
| news                | Anything related to the News app customizer                      |
| profilecard         | Anything related to the Profile Card app customizer              |
| announcement        | Anything related to the Announcement web part                    |
| employeerecognition | Anything related to the Employee Recognition web part            |
| events              | Anything related to the Events web part                          |
| listview            | Anything related to the List View web part                       |
| merge               | Anything related to the Merge web part                           |
| notifications       | Anything related to the Notifications web part                   |
| orgchart            | Anything related to the Org Chart web part                       |
| pagebranding        | Anything related to the Page Branding web part                   |
| peoplesearch        | Anything related to the People Search web part                   |
| personalblog        | Anything related to the Personal Blog web part                   |
| persondisplay       | Anything related to the Person Display web part                  |
| quicklinks          | Anything related to the Quick Links web part                     |
| rotatingbanner      | Anything related to the Rotating Banner web part                 |
| rssfeed             | Anything related to the RSS Feed web part                        |
| submitnews          | Anything related to the Submit News web part                     |
| teammembers         | Anything related to the Team Members web part                    |
| teamvisualiser      | Anything related to the Team Visualiser web part                 |
| welcome             | Anything related to the Welcome web part                         |
| scripteditor        | Anything related to the Script Editor web part                   |
| dailyquiz           | Anything related to the Daily Quiz web part                      |



#### Indicate breaking changes

Add an exclamation mark (!) to your commit message if the change, during deployment, will require manual intervention. 

For example: `feat(api)!: send an email to the customer when a product is shipped`

---

### Isomorphic-fetch

An isomorphic-fetch is an poly-fill to the existing Fetch API. The reason we are using an isomorphic-fetch over the regular fetch is because it is cross-browser compliant.

To use, all you need to do is import the package:
`import "isomorphic-fetch";`

---

### Error Handling

Aim to present a meaningful message to users when an application error occurs. Where possible provide information on remedial actions the user can take to rectify the issue, especially in relation to configuration-related errors. 

Logged errors should provide meaningful information on the error and should at least contain:
- [ ] Error date and time
- [ ] The responsible component or function 
- [ ] Error details (stack trace). Include error messages returned from API responses as well.
- [ ] If you have a need to surface the error in the console, use `console.error()` as these can be interpreted and flagged by the browser.

---

### Code Legibility

Focus on writing readable code rather than attempting to write fewer lines of code (single-line expressions). The code's logic should be easily understood.

Implement functional components (functional development) using the single responsibility principle. If a single component contains a large amount of code, consider breaking it up into separate components each with its own more specific responsibility.

---

### Code Duplication

Focus on eliminating code duplication by implementing reusable functions, components and modules where possible.

---

### Code Formatting

When formatting your code, please ensure you are using [Prettier](https://prettier.io/).

---

### Data Fetching and Mutation

[SWR](https://swr.vercel.app/) has been introduced as a reliable and easy way to manage the fetching of data. It has a built in cache and is easy to implement quickly. It is the expected tool for fetching and mutating data via HTTP requests.

---

### Form States

Instead of using several useStates in a component to manage the state of data, use [react-hook-form](https://react-hook-form.com/) to maintain the state, validation and error handling of form fields. Also use Zod for defining and validating schemas. https://zod.dev/

---

### Dependencies

Third-party libraries introduce a dependency element to a project. Consider using a third-party library if:

- [ ] The library's features will likely be used by more than one function
- [ ] The requirement for the library cannot be easily met using a custom implementation
- [ ] The library introduces multiple features that will be beneficial to the Huddler codebase

When introducing a third-party library, consider the following criteria:

- [ ] The library is actively supported.
- [ ] Adding the library to the code base will not conflict with other packages or the existing setup (will not require a change to existing solution dependencies)
- [ ] The library does not introduce critical security vulnerabilities to the codebase.

---

### Using useEffects

The primary purpose of useEffect is to synchronise a React component with external systems — anything outside of React's state and props. But before using a useEffect please ensure it is absolutely neccessary as there are usually more simple methods/solutions that can be used. If you are unsure, please consult with another member of our team. Please see this article which provides more information: [When to Use and Avoid useEffect in React](https://medium.com/@ignatovich.dm/when-to-use-and-avoid-useeffect-in-react-611e844539a5)

---

