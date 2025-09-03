# Contributing to Public APIs 4 Korea

## Formatting

Current API entry format:

| API | Description | Auth |
| --- | --- | --- |
| API Title(Link to API webpage) | Description of API | Does this API require authentication? * |

Example entry:

```
| [Naver Map](https://www.ncloud.com/product/applicationService/maps) | Map display and address coordinate conversion | `apiKey` |
```

\* Currently, the only accepted inputs for the `Auth` field are as follows:

* `OAuth` - _the API supports OAuth_
* `apiKey` - _the API uses a private key string/token for authentication_
* `JWT` - _the API uses JWT token authentication_
* `Partnership` - _partnership or special contract required_
* `Bearer Token` - _Bearer token authentication required_
* `webhook` - _webhook method is used_
* `No` - _the API requires no authentication to run_

Please add new APIs to the bottom of the relevant category. (We plan to sort alphabetically in the future)

If an API seems to fall into multiple categories, please place the listing within the section most in line with the primary services offered through the API. For example, Kakao Pay API is listed under `Finance & Payment` rather than Social since payment is the main functionality.

## Pull Request

After you've created a branch on your fork with your changes, it's time to make a pull request!

Once you've submitted a pull request, the maintainers can review your proposed changes and decide whether or not to incorporate (pull in) your changes.

* Fork the repository and clone it locally.
  Connect your local repository to the original `upstream` repository by adding it as a remote.
  Pull in changes from `upstream` often so that you stay up to date and so when you submit your pull request, merge conflicts will be less likely.
* Create a branch for your edits.
* Contribute in the style of the project as outlined above. This makes it easier for the maintainers to merge and for others to understand and maintain in the future.

### Open Pull Requests

Once you've opened a pull request, a discussion will start around your proposed changes.

Other contributors and users may chime in, but ultimately the decision is made by the maintainers.

During the discussion, you may be asked to make some changes to your pull request.

If so, add more commits to your branch and push them – they will automatically go into the existing pull request!

### Contribution Guide (Summary)

1. Fork this repository
2. Create a new branch (`git checkout -b (Any branch name)`)
3. Make your code changes
4. Commit your changes (`git commit -am 'Add new API'`)
5. Push to your branch (`git push origin (branch name)`)
6. Open a Pull Request

## Special Considerations

### Korea-Focused APIs
This project focuses on APIs that developers can utilize in Korea:
- Priority for APIs provided by Korean companies/institutions
- Global APIs with Korean language support may be included
- APIs that comply with Korean laws and regulations

### Quality Standards
APIs you want to add should meet the following criteria:
- Publicly available APIs
- APIs with proper documentation
- APIs that provide stable services
- Actually usable APIs (excluding test or beta versions)

### Category Guidelines
Choosing the appropriate category:
- Classify based on the API's primary function
- In ambiguous cases, decide based on the main use case
- If a new category is needed, discuss it in an Issue

Thank you very much for participating in this project!
