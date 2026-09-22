

============================================================
# https://developers.google.com/jules/api/reference/rest
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  Jules API Stay organized with collections  Save and categorize content based on your preferences. 
Programmatically create and access your asynchronous coding tasks.
  * [REST Resource: v1alpha.sessions](https://developers.google.com/jules/api/reference/rest#v1alpha.sessions)
  * [REST Resource: v1alpha.sessions.activities](https://developers.google.com/jules/api/reference/rest#v1alpha.sessions.activities)
  * [REST Resource: v1alpha.sources](https://developers.google.com/jules/api/reference/rest#v1alpha.sources)


## Service: jules.googleapis.com
To call this service, we recommend that you use the Google-provided [client libraries](https://cloud.google.com/apis/docs/client-libraries-explained). If your application needs to use your own libraries to call this service, use the following information when you make the API requests.
### Service endpoint
A [service endpoint](https://cloud.google.com/apis/design/glossary#api_service_endpoint) is a base URL that specifies the network address of an API service. One service might have multiple service endpoints. This service has the following service endpoint and all URIs below are relative to this service endpoint:
  * `https://jules.googleapis.com`


## REST Resource: [v1alpha.sessions](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions)  
| Methods  |  
| --- |  
|   |  `POST /v1alpha/{session=sessions/*}:approvePlan` Approves a plan in a session.  |  
|   |  `POST /v1alpha/sessions` Creates a new session.  |  
|  `GET /v1alpha/{name=sessions/*}` Gets a single session.  |  
|   |  `GET /v1alpha/sessions` Lists all sessions.  |  
|   |  `POST /v1alpha/{session=sessions/*}:sendMessage` Sends a message from the user to a session.  |  
## REST Resource: [v1alpha.sessions.activities](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities)  
| Methods  |  
| --- |  
|  `GET /v1alpha/{name=sessions/*/activities/*}` Gets a single activity.  |  
|  `GET /v1alpha/{parent=sessions/*}/activities` Lists activities for a session.  |  
## REST Resource: [v1alpha.sources](https://developers.google.com/jules/api/reference/rest/v1alpha/sources)  
| Methods  |  
| --- |  
|  `GET /v1alpha/{name=sources/**}` Gets a single source.  |  
|   |  `GET /v1alpha/sources` Lists sources.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-10-02 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  Jules API Stay organized with collections  Save and categorize content based on your preferences. 
Programmatically create and access your asynchronous coding tasks.
  * [REST Resource: v1alpha.sessions](https://developers.google.com/jules/api/reference/rest#v1alpha.sessions)
  * [REST Resource: v1alpha.sessions.activities](https://developers.google.com/jules/api/reference/rest#v1alpha.sessions.activities)
  * [REST Resource: v1alpha.sources](https://developers.google.com/jules/api/reference/rest#v1alpha.sources)


## Service: jules.googleapis.com
To call this service, we recommend that you use the Google-provided [client libraries](https://cloud.google.com/apis/docs/client-libraries-explained). If your application needs to use your own libraries to call this service, use the following information when you make the API requests.
### Service endpoint
A [service endpoint](https://cloud.google.com/apis/design/glossary#api_service_endpoint) is a base URL that specifies the network address of an API service. One service might have multiple service endpoints. This service has the following service endpoint and all URIs below are relative to this service endpoint:
  * `https://jules.googleapis.com`


## REST Resource: [v1alpha.sessions](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions)  
| Methods  |  
| --- |  
|   |  `POST /v1alpha/{session=sessions/*}:approvePlan` Approves a plan in a session.  |  
|   |  `POST /v1alpha/sessions` Creates a new session.  |  
|  `GET /v1alpha/{name=sessions/*}` Gets a single session.  |  
|   |  `GET /v1alpha/sessions` Lists all sessions.  |  
|   |  `POST /v1alpha/{session=sessions/*}:sendMessage` Sends a message from the user to a session.  |  
## REST Resource: [v1alpha.sessions.activities](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities)  
| Methods  |  
| --- |  
|  `GET /v1alpha/{name=sessions/*/activities/*}` Gets a single activity.  |  
|  `GET /v1alpha/{parent=sessions/*}/activities` Lists activities for a session.  |  
## REST Resource: [v1alpha.sources](https://developers.google.com/jules/api/reference/rest/v1alpha/sources)  
| Methods  |  
| --- |  
|  `GET /v1alpha/{name=sources/**}` Gets a single source.  |  
|   |  `GET /v1alpha/sources` Lists sources.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-10-02 UTC.


============================================================
# https://cloud.google.com/apis/design/glossary
============================================================

#### AIP-9
# Glossary
In the name of brevity, this AIP defines some common terminology here rather than in each AIP individually.
## Guidance
The following terminology **should** be used consistently throughout AIPs.
### API
Application programming interface. This can be a local interface (such as a client library) or a Network API (defined below).
### API backend
A set of servers and related infrastructure that implements the business logic for an API service. An individual API backend server is often called an API server.
### API consumer
The entity that consumes an API service. For Google APIs, it typically is a Google project that owns the client application or the server resource.
### API definition
The definition of an API, usually defined in a Protocol Buffer service. An API definition can be implemented by any number of API services.
### API frontend
A set of servers plus related infrastructure that provides common functionality across API services, such as load balancing and authentication. An individual API frontend server is often called an API proxy.
**Note:** the API frontend and the API backend may run next to each other or far away from each other. In some cases, they can be compiled into a single application binary and run inside a single process.
### API interface
The element of an API specification IDL that groups API methods, such as a Protocol Buffers `service` definition. It is typically mapped to a similar high level grouping mechanism in most programming languages, like a `class` or `interface`.
### API interface version
A distinct iteration of an API interface represented by an API version identifier. A constituent part of an [API service version](https://google.aip.dev/9#api-service-version).
### API method
An individual operation within an API. It is typically represented in Protocol Buffers by an `rpc` definition, and is mapped to a function in the API in most programming languages.
### API producer
The entity that produces an API service. For Google APIs, it typically is a Google team responsible for the API service.
### API product
An API service and its related components, such as Terms of Service, documentation, client libraries, and service support, are collectively presented to customers as a API product. For example, Google Calendar API.
**Note:** people sometimes refer to an API product simply as an API.
### API service
A deployed implementation of one or more APIs, exposed on one or more network addresses, such as the Cloud Pub/Sub API.
### API service definition
The combination of API definitions (`.proto` files) and API service configurations (`.yaml` files) used to define an API service. The schema for Google API service definition is `google.api.Service`.
### API service endpoint
Refers to a network address that an API service uses to handle incoming API requests. One API service may have multiple API service endpoints, such as `https://pubsub.googleapis.com` and `https://content-pubsub.googleapis.com`.
### API service name
Refers to the logical identifier of an API service. Google APIs use RFC 1035 DNS compatible names as their API service names, such as `pubsub.googleapis.com`.
### API service version
A distinct set of API interfaces and their contemporaneous API interface versions. It is scoped to an API variant. The API service version value is typically equal to the latest API interface version in that set. The content of API artifacts, such as reference documentation, client library packages, and other API-based tooling, are often organized around one or more service versions.
### API title
Refers to the user-facing product title of an API service, such as "Cloud Pub/Sub API".
### API request
A single invocation of an API method. It is often used as the unit for billing, logging, monitoring, and rate limiting.
### API variant
The top-level iteration of an API, such as "v1beta" or "v2", that appears in API artifacts such as specifications, client packages, and folder-filesystem structure. API variants are producer-defined shorthands that demarcate side-by-side namespaces for API interface versions.
### API version
API version is used colloquially in reference to any of the following:
  * In channel-based versioning, it refers to the [API variant](https://google.aip.dev/9#api-variant).
  * In interface-based versioning, it can refer to any of the following:
    * [API interface version](https://google.aip.dev/9#api-interface-version)
    * [API service version](https://google.aip.dev/9#api-service-version)
    * [API version identifier](https://google.aip.dev/9#api-version-identifier)


Prefer to use the more specific term wherever possible.
### API version identifier
The name of a versioned iteration of an API interface, such as `2024-10-31`. It is the "key" to clients and services communicating via the same API. See [AIP-184](https://aip.dev/184) for more detail on version identifiers.
### Client
Clients are programs that perform a specific tasks by calling an API or generic tools, such as CLIs, that expose the API in a user-accessible fashion or operate on resource data at rest.
Examples of clients include the following:
  * Command line interfaces
  * Libraries, such as an SDK for a particular programming language
  * Scripts that operates on a JSON representation of a resource after reading it from an API
  * Tools, such as a [Declarative clients](https://google.aip.dev/9#declarative-clients)
  * Visual UIs, such as a web application


### Google API
A Network API exposed by a Google service. Most of these are hosted on the `googleapis.com` domain. It does not include other types of APIs, such as client libraries and SDKs.
### Declarative Clients
Declarative Clients, also known as Infrastructure as Code (IaC), describes a category of clients that consumes a markup language or code that represents resources exposed by an API, and executes the appropriate imperative actions to drive the resource to that desired state. To determine what changes to make and if a set of updates was successful a declarative client compares server side resource attributes with client defined values. The comparison feature ensures accuracy of a creation or an update but it requires services to treat the client set fields as read-only and diligently preserve those values.
Examples of complexities that declarative clients abstract away include:
  * Determining the appropriate imperative action (create / update / delete) to achieve desired state.
  * Ordering of these imperative actions.


[Terraform](https://www.terraform.io/) is an example of such a client.
### User
A human being which is using an API directly, such as with cURL. This term is defined to differentiate usage in the AIPs between a human _user_ and a programmatic _client_.
### Network API
An API that operates across a network of computers. Network APIs communicate using network protocols including HTTP, and are frequently produced by organizations separate from those that consume them.
## Changelog
  * **2026-08-17** : Add Interface-Based Versioning glossary terms.
  * **2025-08-13** : Add API inteface entry
  * **2024-12-18** : Downcase headings and terms as per dev docs style
  * **2024-10-23** : Add API Title entry
  * **2023-07-24** : Rename IaC to Declarative Clients
  * **2023-04-01** : Adding definition of IaC
  * **2023-03-24** : Reformatting content to include anchor links.




============================================================
# https://developers.google.com/
============================================================

[ Skip to main content ](https://developers.google.com/#main-content)
  * English
  * Deutsch
  * Español
  * Español – América Latina
  * Français
  * Indonesia
  * Italiano
  * Português – Brasil
  * Tiếng Việt
  * Русский
  * العربيّة
  * ภาษาไทย
  * 中文 – 简体
  * 中文 – 繁體

Sign in


Stay organized with collections  Save and categorize content based on your preferences. 
# Build with Gemini
Unlock AI models to build innovative apps and transform development workflows with tools across platforms.
pen_spark Start building with Gemini expand_content
The fastest path from prompt to production app with Gemini.
code Develop with agents expand_content
Experience our agent-first platform built for the next era of how you build, work, and automate.
automatic_cluster Deploy on scalable infrastructure expand_content
Build and scale your apps without needing to manage the infrastructure with Google Cloud Run.
android Create Android apps expand_content
Build high-quality Android apps faster with Gemini in Android Studio.
sort_spark Build apps and agents with Gemini models expand_content
Develop next-generation apps and agents by integrating Google's most advanced reasoning and generative models and agent-first APIs.
web Develop web AI features expand_content
Discover how your web applications can perform AI tasks with browser-managed AI models and APIs.
stacks Build enterprise agents expand_content
Build, scale, govern, and optimize enterprise agents.
close
GEMINI API
## Integrate Gemini directly into your apps
Unleash the full potential of your applications by integrating Gemini's long context window and native multimodal reasoning to process massive codebases, complex media, and real-time agentic workflows with a single API.
[View documentation](https://ai.google.dev/gemini-api/docs)

```
fromgoogleimport genai

client = genai.Client()

response = client.models.generate_content(
  model="gemini-3.5-flash",
  contents="Explain how AI works in a few words",
)

print(response.text)
```

```
import{GoogleGenAI}from"@google/genai";

constai=newGoogleGenAI({});

asyncfunctionmain(){
constresponse=awaitai.models.generateContent({
model:"gemini-3.5-flash",
contents:"Explain how AI works in a few words",
});
console.log(response.text);
}

awaitmain();
```

```
packagemain

import(
"context"
"fmt"
"log"
"google.golang.org/genai"
)

funcmain(){
ctx:=context.Background()
client,err:=genai.NewClient(ctx,nil)
iferr!=nil{
log.Fatal(err)
}

result,err:=client.Models.GenerateContent(
ctx,
"gemini-3.5-flash",
genai.Text("Explain how AI works in a few words"),
nil,
)
iferr!=nil{
log.Fatal(err)
}
fmt.Println(result.Text())
}
```

```
packagecom.example;

importcom.google.genai.Client;
importcom.google.genai.types.GenerateContentResponse;

publicclass GenerateTextFromTextInput{
publicstaticvoidmain(String[]args){
Clientclient=newClient();

GenerateContentResponseresponse=
client.models.generateContent(
"gemini-3.5-flash",
"Explain how AI works in a few words",
null);

System.out.println(response.text());
}
}
```

```
curl"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-5-flash:generateContent"\
-H"x-goog-api-key: $GEMINI_API_KEY"\
-H'Content-Type: application/json'\
-XPOST\
-d'{
    "contents": [

        "parts": [

            "text": "Explain how AI works in a few words"




  }'
```

## News & Announcements
Google Play
New quality requirements on Google Play
add remove
Raising the quality bar: Prepare for new Play standards in memory, code, and onboarding.
[Learn more](https://android-developers.googleblog.com/2026/08/app-quality-memory-optimization-secure-onboarding.html)
AI Agents
Treat agent prompts like software artifacts
add remove
Use build-time validation and modular architectures to make your agents production-ready.
[Learn more](https://developers.googleblog.com/building-scalable-ai-agents-with-modular-prompt-transpilation/)
Google Play
Play billing and fee updates
add remove
Google Play is evolving from a standard billing system to a flexible ecosystem built for high-quality experiences. Learn how to set the new standard for user experience and unlock lower rates.
[Learn more](https://goo.gle/playdev-q3-updates)
Antigravity CLI
Gemini CLI Transitions to Antigravity CLI
add remove
Discover the new Antigravity CLI and migrate by June 18
[Learn more](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
## Community & Events
[ Google I/O Connect I/O Connect China Connect with fellow professional developers and Google experts, get inspired by the latest tools and tech, accelerate your development, and create cutting-edge applications. August 12-13 / Shanghai ](https://ioconnectchina.googlecnapps.cn/intl/en_cn/) [ Google Cloud Build with Gemini Move beyond basic chatbots. Join Google Cloud experts for a hands-on day building, scaling, and deploying secure, production-ready AI agents. Aug - Oct / Multi-city ](https://cloud.google.com/events/build-with-gemini-2026?e=48754805) [ Google Cloud Google Cloud Summit Doha Join the annual Google Cloud event to discover the latest technological innovations in AI, security, application development, collaboration, and more. September 22 / Doha, Qatar ](https://cloudonair.withgoogle.com/events/google-cloud-summit-doha-2026-qncc)
## Build and manage in one place
Access specialized AI workspaces, learn from 700+ hands-on codelabs, and manage projects from a centralized Builders Hub as you move from prototype to production.
[Join the program](https://developers.google.com/program)


============================================================
# https://cloud.google.com/apis/docs/client-libraries-explained
============================================================

[ Skip to main content ](https://docs.cloud.google.com/apis/docs/client-libraries-explained#main-content)
[ Console ](https://console.cloud.google.com/)
  * English
  * Deutsch
  * Español
  * Español – América Latina
  * Français
  * Indonesia
  * Italiano
  * Português
  * Português – Brasil
  * 中文 – 简体
  * 中文 – 繁體

Sign in




Send feedback 
#  Client libraries and Cloud APIs explained Stay organized with collections  Save and categorize content based on your preferences. 
While you can use Google Cloud APIs directly by making raw requests to the server, client libraries provide simplifications that significantly reduce the amount of code you need to write.
This document explains methods for interacting with Google Cloud APIs:
  * Cloud Client Libraries (recommended)
  * Google API Client Libraries
  * Firebase mobile
  * Your own client code


To find client library information for a specific Google Cloud product, see the client libraries section within that product's documentation. To view all Cloud Client Libraries, often organized by supported language, see [Cloud Client Libraries](https://docs.cloud.google.com/apis/docs/cloud-client-libraries).
## Cloud Client Libraries
[Cloud Client Libraries](https://docs.cloud.google.com/apis/docs/cloud-client-libraries) are the recommended option for accessing Cloud APIs programmatically, where available. Cloud Client Libraries use the latest client library model and:
  * Provide idiomatic code in each language to make Google Cloud APIs intuitive to use.
  * Provide a consistent style across client libraries to simplify working with multiple Google Cloud services.
  * Handle all the low-level details of communication with the server, including [authenticating with Google](https://docs.cloud.google.com/docs/authentication/client-libraries).
  * Can be installed using familiar package management tools such as `npm` and `pip`.
  * In some cases, give you performance benefits by using gRPC. For more information, see [gRPC APIs](https://docs.cloud.google.com/apis/docs/client-libraries-explained#grpc_apis).


The installation instructions and reference materials for Cloud Client Libraries depend on the specific Google Cloud API and the programming language you are using. To find this information, see the documentation for the specific Google Cloud product. Most products include a "Client Libraries" section in their documentation, which provides language-specific guidance, installation steps, and links to the detailed API reference.
You can find the documentation for a specific product by browsing the [Google Cloud API library](https://docs.cloud.google.com/apis).
##  Try it for yourself 
If you're new to Google Cloud, create an account to evaluate how our products perform in real-world scenarios. New customers also get $300 in free credits to run, test, and deploy workloads. 
[ Get started for free ](https://console.cloud.google.com/freetrial)
## Google API Client Libraries
If Cloud Client Libraries aren't available for your preferred language for a specific API, you can use the [Google API Client Libraries](https://developers.google.com/api-client-library/). These are an earlier type of client library provided by Google.
You might also use these libraries if you're upgrading a project that already uses them. These libraries:
  * Provide access to the API's REST interface only; gRPC is not supported.
  * Have auto-generated interface code that might not be as idiomatic as the Cloud Client Libraries.
  * Handle all the low-level details of communication with the server, including [authenticating with Google](https://docs.cloud.google.com/docs/authentication/client-libraries).
  * Can be installed using familiar package management tools such as `npm` and `pip`.


## Use the Firebase development platform
Firebase is Google's platform of services designed to support your entire app development lifecycle. It provides cross-platform SDKs to help you and AI agents build and run apps for Apple platforms, Android, the web, Flutter, Unity, and C++.
For information on the supported Google Cloud APIs and how to get started with Firebase, see the [Firebase documentation](https://firebase.google.com/docs).
## Use your own client code
If you're an experienced developer and Cloud Client Libraries don't meet your specific needs, you can write your own custom code to access the service's lower-level service APIs directly.
### REST/HTTP APIs
All Google Cloud APIs expose a JSON/REST interface. If you need to write your own custom code to directly access the REST API using a third-party HTTP client library, you can find out more about how Google Cloud APIs work with different HTTP versions and implementations in the [HTTP Guidelines](https://docs.cloud.google.com/apis/docs/http).
### gRPC APIs
gRPC is a language-neutral, platform-neutral, open source, remote procedure call (RPC) system initially developed at Google. You can find out more at [grpc.io](http://www.grpc.io/). gRPC-enabled Google Cloud APIs generally have both REST and RPC interfaces, so rather than just using JSON over HTTP to talk to the REST interface, gRPC-enabled API clients can also use [protocol buffers](https://developers.google.com/protocol-buffers/) and gRPC over HTTP2 to talk to the RPC interface. You can find out if an API is gRPC-enabled by checking its APIs and Reference section.
If a Google Cloud API is gRPC-enabled, you can generate your own gRPC client libraries for it in any gRPC-supported language. To do this, you'll need the API's [protocol buffers](https://developers.google.com/protocol-buffers/) service definition (typically available from [the repository on GitHub](https://github.com/googleapis/googleapis)).
You can then follow the instructions for your preferred language on [grpc.io](http://www.grpc.io/) to generate and use your client.
If you don't want to generate your own gRPC code, you can still benefit from gRPC: a growing number of Cloud Client Libraries for gRPC-enabled APIs use gRPC "under the hood" to communicate with Google's servers. This is significantly more efficient in terms of throughput and CPU usage—accessing an API using gRPC can increase throughput per CPU by as much as a factor of 10 compared to the JSON REST API. Google plans to upgrade as many Cloud Client Libraries as possible to gRPC; in the meantime, you'll still get all the other advantages of Google's client library code.
## Other ways to access Cloud APIs
If you don't want to access an API programmatically, you can access some of the same functionality using the tools in [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs) or using the [Google Cloud console](https://console.cloud.google.com/). 
Send feedback 
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-09-21 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#main-content)



Sign in
  * On this page
  * [Methods](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#methods)




#  REST Resource: sessions Stay organized with collections  Save and categorize content based on your preferences.
  * On this page
  * [Methods](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#methods)


  * [Resource: Session](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#Session)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#Session.SCHEMA_REPRESENTATION)
  * [SourceContext](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#SourceContext)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#SourceContext.SCHEMA_REPRESENTATION)
  * [GitHubRepoContext](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#GitHubRepoContext)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#GitHubRepoContext.SCHEMA_REPRESENTATION)
  * [AutomationMode](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#AutomationMode)
  * [SessionOutput](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#SessionOutput)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#SessionOutput.SCHEMA_REPRESENTATION)
  * [PullRequest](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#PullRequest)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions#PullRequest.SCHEMA_REPRESENTATION)


## Resource: Session
A session is a contiguous amount of work within the same context.  
| JSON representation  |  
| --- |  
| 
```
{
  "name": string,
  "id": string,
  "prompt": string,
  "sourceContext": {
    object ()
  },
  "title": string,
  "requirePlanApproval": boolean,
  "automationMode": enum (),
  "createTime": string,
  "updateTime": string,
  "state": enum (),
  "url": string,
  "outputs": [
    {
      object ()
    }
  ]
}
```
 |  
| Fields  |  
| --- |  
| `name`  |  `string` Output only. Identifier. The full resource name (e.g., "sessions/{session}").  |  
|  `string` Output only. The id of the session. This is the same as the "{session}" part of the resource name (e.g., "sessions/{session}").  |  
| `prompt`  |  `string` Required. The prompt to start the session with.  |  
| `sourceContext`  |  `object ()` Required. The source to use in this session, with additional context.  |  
| `title`  |  `string` Optional. If not provided, the system will generate one.  |  
| `requirePlanApproval`  |  `boolean` Optional. Input only. If true, plans the agent generates will require explicit plan approval before the agent starts working. If not set, plans will be auto-approved.  |  
| `automationMode`  |  `enum ()` Optional. Input only. The automation mode of the session. If not set, the default automation mode will be used.  |  
| `createTime`  |  `string ( format)` Output only. The time the session was created. Uses RFC 3339, where generated output will always be Z-normalized and use 0, 3, 6 or 9 fractional digits. Offsets other than "Z" are also accepted. Examples: `"2014-10-02T15:01:23Z"`, `"2014-10-02T15:01:23.045123456Z"` or `"2014-10-02T15:01:23+05:30"`.  |  
| `updateTime`  |  `string ( format)` Output only. The time the session was last updated. Uses RFC 3339, where generated output will always be Z-normalized and use 0, 3, 6 or 9 fractional digits. Offsets other than "Z" are also accepted. Examples: `"2014-10-02T15:01:23Z"`, `"2014-10-02T15:01:23.045123456Z"` or `"2014-10-02T15:01:23+05:30"`.  |  
| `state`  |  `enum ()` Output only. The state of the session.  |  
| `url`  |  `string` Output only. The URL of the session to view the session in the Jules web app.  |  
| `outputs[]`  |  `object ()` Output only. The outputs of the session, if any.  |  
## SourceContext
Context for how to use a source in a session.  
| JSON representation  |  
| --- |  
| 
```
{
  "source": string,

  // Union field context can be only one of the following:
  "githubRepoContext": {
    object ()
  }
  // End of list of possible types for union field context.
}
```
 |  
| Fields  |  
| --- |  
| `source`  |  `string` Required. The name of the source this context is for. To get the list of sources, use the ListSources API. Format: sources/{source}  |  
| Union field `context`. The context for how to use the source in a session. `context` can be only one of the following:  |  
| `githubRepoContext`  |  `object ()` Context to use a GitHubRepo in a session.  |  
## GitHubRepoContext
Context to use a GitHubRepo in a session.  
| JSON representation  |  
| --- |  
| 
```
{
  "startingBranch": string
}
```
 |  
| Fields  |  
| --- |  
| `startingBranch`  |  `string` Required. The name of the branch to start the session from.  |  
## AutomationMode
The automation mode of the session.  
| Enums  |  
| --- |  
| `AUTOMATION_MODE_UNSPECIFIED`  | The automation mode is unspecified. Default to no automation.  |  
| `AUTO_CREATE_PR`  | Whenever a final code patch is generated in the session, automatically create a branch and a pull request for it, if applicable.  |  
## State
State of a session.  
| Enums  |  
| --- |  
| `STATE_UNSPECIFIED`  | The state is unspecified.  |  
| `QUEUED`  | The session is queued.  |  
| `PLANNING`  | The agent is planning.  |  
| `AWAITING_PLAN_APPROVAL`  | The agent is waiting for plan approval.  |  
| `AWAITING_USER_FEEDBACK`  | The agent is waiting for user feedback.  |  
| `IN_PROGRESS`  | The session is in progress.  |  
| `PAUSED`  | The session is paused.  |  
| `FAILED`  | The session has failed.  |  
| `COMPLETED`  | The session has completed.  |  
## SessionOutput
An output of a session.  
| JSON representation  |  
| --- |  
| 
```
{

  // Union field output can be only one of the following:
  "pullRequest": {
    object ()
  }
  // End of list of possible types for union field output.
}
```
 |  
| Fields  |  
| --- |  
| Union field `output`. An output of the session. `output` can be only one of the following:  |  
| `pullRequest`  |  `object ()` A pull request created by the session, if applicable.  |  
## PullRequest
A pull request.  
| JSON representation  |  
| --- |  
| 
```
{
  "url": string,
  "title": string,
  "description": string
}
```
 |  
| Fields  |  
| --- |  
| `url`  |  `string` The URL of the pull request.  |  
| `title`  |  `string` The title of the pull request.  |  
| `description`  |  `string` The description of the pull request.  |  
| 
## Methods
 |  
| --- |  
| 
### 
 |  Approves a plan in a session.  |  
| 
### 
 |  Creates a new session.  |  
|  Gets a single session.  |  
|  Lists all sessions.  |  
| 
### 
 |  Sends a message from the user to a session.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-10-07 UTC.


============================================================
# https://developers.google.com/jules/api
============================================================

[ Skip to main content ](https://developers.google.com/jules/api#main-content)


  * [Português – Brasil](https://developers.google.com/jules/api?hl=pt-br)

Sign in
  * On this page
  * [Authentication](https://developers.google.com/jules/api#authentication)
  * [Quickstart: Your first API call](https://developers.google.com/jules/api#quickstart:-your-first-api-call)
    * [Step 1: List your available sources](https://developers.google.com/jules/api#step-1:-list-your-available-sources)
    * [Step 2: Create a new session](https://developers.google.com/jules/api#step-2:-create-a-new-session)
    * [Step 3: Listing sessions](https://developers.google.com/jules/api#step-3:-listing-sessions)
    * [Step 5: Activities and interacting with the agent](https://developers.google.com/jules/api#step-5:-activities-and-interacting-with-the-agent)




#  Jules API Stay organized with collections  Save and categorize content based on your preferences.
  * On this page
  * [Authentication](https://developers.google.com/jules/api#authentication)
  * [Quickstart: Your first API call](https://developers.google.com/jules/api#quickstart:-your-first-api-call)
    * [Step 1: List your available sources](https://developers.google.com/jules/api#step-1:-list-your-available-sources)
    * [Step 2: Create a new session](https://developers.google.com/jules/api#step-2:-create-a-new-session)
    * [Step 3: Listing sessions](https://developers.google.com/jules/api#step-3:-listing-sessions)
    * [Step 5: Activities and interacting with the agent](https://developers.google.com/jules/api#step-5:-activities-and-interacting-with-the-agent)


## Introduction
The Jules API lets you programmatically access Jules's capabilities to automate and enhance your software development lifecycle. You can use the API to create custom workflows, automate tasks like bug fixing and code reviews, and embed Jules's intelligence directly into the tools you use every day, such as Slack, Linear, and GitHub. 
## Authentication
To get started with the Jules API, you'll need an API key.
### Generate Your API Key
In the Jules web app, go to the page to create a new API key. You can have at most 3 API keys at a time.
### Use Your API Key
To authenticate your requests, pass the API key in the `X-Goog-Api-Key` header of your API calls.
## API concepts
The Jules API is built around a few core resources. Understanding these will help you use the API effectively. 

**Source**
    An input source for the agent (e.g., a GitHub repository). Before using a source using the API, you must first [install the Jules GitHub app](https://jules.google/docs) through the Jules web app. 

**Session**
    A continuous unit of work within a specific context, similar to a chat session. A session is initiated with a prompt and a source. 

**Activity**
    A single unit of work within a Session. A Session contains multiple activities from both the user and the agent, such as generating a plan, sending a message, or updating progress.
## Quickstart: Your first API call
We'll walk through creating your first session with the Jules API using curl.
### Step 1: List your available sources
First, you need to find the name of the source you want to work with (e.g., your GitHub repo). This command will return a list of all sources you have connected to Jules.

```
curl 'https://jules.googleapis.com/v1alpha/sources' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

The response will look something like this:

```
{
  "sources": [
    {
      "name": "sources/github/bobalover/boba",
      "id": "github/bobalover/boba",
      "githubRepo": {
        "owner": "bobalover",
        "repo": "boba"
      }
    }
  ],
  "nextPageToken": "github/bobalover/boba-web"
}
```

### Step 2: Create a new session
Now, create a new session. You'll need the source name from the previous step. This request tells Jules to create a boba app in the specified repository.

```
curl 'https://jules.googleapis.com/v1alpha/sessions' \
    -X POST \
    -H "Content-Type: application/json" \
    -H 'X-Goog-Api-Key: YOUR_API_KEY' \
    -d '{
      "prompt": "Create a boba app!",
      "sourceContext": {
        "source": "sources/github/bobalover/boba",
        "githubRepoContext": {
          "startingBranch": "main"
        }
      },
      "automationMode": "AUTO_CREATE_PR",
      "title": "Boba App"
    }'
```

The `automationMode` field is optional. By default, no PR will be automatically created.
The immediate response will look something like this:

```
{
        "name": "sessions/31415926535897932384",
        "id": "31415926535897932384",
        "title": "Boba App",
        "sourceContext": {
          "source": "sources/github/bobalover/boba",
          "githubRepoContext": {
            "startingBranch": "main"
          }
        },
        "prompt": "Create a boba app!"
      }
```

You can poll the latest session information using GetSession or ListSessions. For example, if a PR was automatically created, you can see the PR in the session output.

```
{
  "name": "sessions/31415926535897932384",
  "id": "31415926535897932384",
  "title": "Boba App",
  "sourceContext": {
    "source": "sources/github/bobalover/boba",
    "githubRepoContext": {
      "startingBranch": "main"
    }
  },
  "prompt": "Create a boba app!",
  "outputs": [
    {
      "pullRequest": {
        "url": "https://github.com/bobalover/boba/pull/35",
        "title": "Create a boba app",
        "description": "This change adds the initial implementation of a boba app."
      }
    }
  ]
}
    
```

By default, sessions created through the API will have their plans automatically approved. If you want to create a session that requires explicit plan approval, set the `requirePlanApproval` field to `true`.
### Step 3: Listing sessions
You can list your sessions as follows.

```
curl 'https://jules.googleapis.com/v1alpha/sessions?pageSize=5' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

### Step 4: Approve plan
If your session requires explicit plan approval, you can approve the latest plan as follows:

```
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:approvePlan' \
    -X POST \
    -H "Content-Type: application/json" \
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

### Step 5: Activities and interacting with the agent
To list activities in a session:

```
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities?pageSize=30' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

To send a message to the agent:

```
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage' \
    -X POST \
    -H "Content-Type: application/json" \
    -H 'X-Goog-Api-Key: YOUR_API_KEY' \
    -d '{
      "prompt": "Can you make the app corgi themed?"
    }'
```
The response will be empty because the agent will send its response in the next activity. To see the agent's response, list the activities again. 
Here is an example of a ListActivities response.

```
{
  "activities": [
    {
      "name": "sessions/14550388554331055113/activities/02200cce44f746308651037e4a18caed",
      "createTime": "2025-10-03T05:43:42.801654Z",
      "originator": "agent",
      "planGenerated": {
        "plan": {
          "id": "5103d604240042cd9f59a4cb2355643a",
          "steps": [
            {
              "id": "705a61fc8ec24a98abc9296a3956fb6b",
              "title": "Setup the environment. I will install the dependencies to run the app."
            },
            {
              "id": "bb5276efad354794a4527e9ad7c0cd42",
              "title": "Modify `src/App.js`. I will replace the existing React boilerplate with a simple Boba-themed component. This will include a title and a list of boba options.",
              "index": 1
            },
            {
              "id": "377c9a1c91764dc794a618a06772e3d8",
              "title": "Modify `src/App.css`. I will update the CSS to provide a fresh, modern look for the Boba app.",
              "index": 2
            },
            {
              "id": "335802b585b449aeabb855c722cd9c40",
              "title": "Frontend Verification. I will use the `frontend_verification_instructions` tool to get instructions on how to write a Playwright script to verify the frontend application and generate a screenshot of the changes.",
              "index": 3
            },
            {
              "id": "3e4cc97c7b2448668d1ac75b8c7b7d69",
              "title": "Submit the changes. Once the app is looking good and verified, I will submit my work.",
              "index": 4
            }
          ]
        }
      },
      "id": "02200cce44f746308651037e4a18caed"
    },
    {
      "name": "sessions/14550388554331055113/activities/2918fac8bc54450a9cbda423b7688413",
      "createTime": "2025-10-03T05:43:44.954030Z",
      "originator": "user",
      "planApproved": {
        "planId": "5103d604240042cd9f59a4cb2355643a"
      },
      "id": "2918fac8bc54450a9cbda423b7688413"
    },
    {
      "name": "sessions/14550388554331055113/activities/5b3acd1b3ca2439f9cbaefaccf7f709a",
      "createTime": "2025-10-03T05:44:16.700231Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "Ran bash command",
        "description": "Command: \nnpm install\nOutput: added 1326 packages, and audited 1327 packages in 25s\n\n268 packages are looking for fundingExit Code: 0"
      },
      "artifacts": [
        {
          "bashOutput": {
            "command": "\nnpm install",
            "output": "added 1326 packages, and audited 1327 packages in 25s\n\n268 packages are looking for funding"
          }
        }
      ],
      "id": "5b3acd1b3ca2439f9cbaefaccf7f709a"
    },
    {
      "name": "sessions/14550388554331055113/activities/1ad545d812614a5b84c23a33f6120063",
      "createTime": "2025-10-03T05:44:19.502115Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "I have installed the dependencies using `npm install`."
      },
      "artifacts": [
        {
          "changeSet": {
            "source": "sources/github/bobalover/boba",
            "gitPatch": {
              "baseCommitId": "36ead0a4caefc451b9652ed926a15af9570f4f35"
            }
          }
        }
      ],
      "id": "1ad545d812614a5b84c23a33f6120063"
    },
    {
      "name": "sessions/14550388554331055113/activities/3a2b46329f894ebea1faf6b8fb956428",
      "createTime": "2025-10-03T05:44:29.265425Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "I have replaced the boilerplate in `src/App.js` with a Boba-themed component."
      },
      "artifacts": [
        {
          "changeSet": {
            "source": "sources/github/bobalover/boba",
            "gitPatch": {
              "unidiffPatch": "",
              "baseCommitId": "36ead0a4caefc451b9652ed926a15af9570f4f35"
            }
          }
        }
      ],
      "id": "3a2b46329f894ebea1faf6b8fb956428"
    },
    {
      "name": "sessions/14550388554331055113/activities/4e8dd66f15e247e3ae5e48eeff89ef47",
      "createTime": "2025-10-03T05:44:37.721013Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "I have updated the CSS in `src/App.css` to give the app a fresh, modern look."
      },
      "artifacts": [
        {
          "changeSet": {
            "source": "sources/github/bobalover/boba",
            "gitPatch": {
              "unidiffPatch": ""
            }
          }
        }
      ],
      "id": "4e8dd66f15e247e3ae5e48eeff89ef47"
    },
    {
      "name": "sessions/14550388554331055113/activities/100901155a4141d3b37e8e8d2950f3b7",
      "createTime": "2025-10-03T05:44:51.048996Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "Ran bash command",
        "description": "Command: \nOutput: Command failed due to an internal error.\nExit Code: 1"
      },
      "artifacts": [
        {
          "bashOutput": {
            "output": "Command failed due to an internal error.",
            "exitCode": 1
          }
        }
      ],
      "id": "100901155a4141d3b37e8e8d2950f3b7"
    },
    {
      "name": "sessions/14550388554331055113/activities/a76b35353eda42d09b1c37aedaa56047",
      "createTime": "2025-10-03T05:47:49.628363Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "Frontend verification",
        "description": "Agent provided UI verification."
      },
      "artifacts": [
        {
          "media": {
            "data": "",
            "mimeType": "image/png"
          }
        }
      ],
      "id": "a76b35353eda42d09b1c37aedaa56047"
    },
    {
      "name": "sessions/14550388554331055113/activities/db089c7052024cbeb9e37b8c584bc964",
      "createTime": "2025-10-03T05:47:53.669642Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "I have successfully verified the frontend changes by building the app, runnin...",
        "description": "I have successfully verified the frontend changes by building the app, running a Playwright script, and inspecting the resulting screenshot."
      },
      "artifacts": [
        {
          "changeSet": {
            "source": "sources/github/bobalover/boba",
            "gitPatch": {
              "unidiffPatch": "",
              "baseCommitId": "36ead0a4caefc451b9652ed926a15af9570f4f35"
            }
          }
        }
      ],
      "id": "db089c7052024cbeb9e37b8c584bc964"
    },
    {
      "name": "sessions/14550388554331055113/activities/890e16e30dbb4bf99a92613bdccec212",
      "createTime": "2025-10-03T05:48:14.434427Z",
      "originator": "agent",
      "progressUpdated": {
        "title": "Code reviewed",
        "description": "The user wants to create a \"boba app\". This is a very open-ended request, but the agent's implementation suggests the goal is to create a simple, static web page about boba."
      },
      "id": "890e16e30dbb4bf99a92613bdccec212"
    },
    {
      "name": "sessions/14550388554331055113/activities/022837dbc0e940eabcc1bc53608e15fc",
      "createTime": "2025-10-03T05:48:35.523200Z",
      "originator": "agent",
      "sessionCompleted": {},
      "artifacts": [
        {
          "changeSet": {
            "source": "sources/github/bobalover/boba",
            "gitPatch": {
              "unidiffPatch": "",
              "baseCommitId": "36ead0a4caefc451b9652ed926a15af9570f4f35",
              "suggestedCommitMessage": "feat: Create simple Boba App\n\nThis commit transforms the default Create React App boilerplate into a simple, visually appealing Boba-themed application."
            }
          }
        }
      ],
      "id": "022837dbc0e940eabcc1bc53608e15fc"
    }
  ]
}

```

## Full API reference
View the full [API reference](https://developers.google.com/jules/api/reference/rest) documentation for the Jules API.
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-11-10 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#main-content)



Sign in
  * On this page
  * [Methods](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#methods)




#  REST Resource: sessions.activities Stay organized with collections  Save and categorize content based on your preferences.
  * On this page
  * [Methods](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#methods)


  * [Resource: Activity](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Activity)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Activity.SCHEMA_REPRESENTATION)
  * [AgentMessaged](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#AgentMessaged)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#AgentMessaged.SCHEMA_REPRESENTATION)
  * [UserMessaged](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#UserMessaged)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#UserMessaged.SCHEMA_REPRESENTATION)
  * [PlanGenerated](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#PlanGenerated)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#PlanGenerated.SCHEMA_REPRESENTATION)
  * [Plan](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Plan)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Plan.SCHEMA_REPRESENTATION)
  * [PlanStep](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#PlanStep)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#PlanStep.SCHEMA_REPRESENTATION)
  * [PlanApproved](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#PlanApproved)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#PlanApproved.SCHEMA_REPRESENTATION)
  * [ProgressUpdated](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#ProgressUpdated)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#ProgressUpdated.SCHEMA_REPRESENTATION)
  * [SessionCompleted](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#SessionCompleted)
  * [SessionFailed](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#SessionFailed)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#SessionFailed.SCHEMA_REPRESENTATION)
  * [Artifact](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Artifact)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Artifact.SCHEMA_REPRESENTATION)
  * [ChangeSet](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#ChangeSet)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#ChangeSet.SCHEMA_REPRESENTATION)
  * [GitPatch](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#GitPatch)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#GitPatch.SCHEMA_REPRESENTATION)
  * [Media](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Media)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#Media.SCHEMA_REPRESENTATION)
  * [BashOutput](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#BashOutput)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities#BashOutput.SCHEMA_REPRESENTATION)


## Resource: Activity
An activity is a single unit of work within a session.  
| JSON representation  |  
| --- |  
| 
```
{
  "name": string,
  "id": string,
  "description": string,
  "createTime": string,
  "originator": string,
  "artifacts": [
    {
      object ()
    }
  ],

  // Union field activity can be only one of the following:
  "agentMessaged": {
    object ()
  },
  "userMessaged": {
    object ()
  },
  "planGenerated": {
    object ()
  },
  "planApproved": {
    object ()
  },
  "progressUpdated": {
    object ()
  },
  "sessionCompleted": {
    object ()
  },
  "sessionFailed": {
    object ()
  }
  // End of list of possible types for union field activity.
}
```
 |  
| Fields  |  
| --- |  
| `name`  |  `string` Identifier. The full resource name (e.g., "sessions/{session}/activities/{activity}").  |  
|  `string` Output only. The id of the activity. This is the same as the "{activity}" part of the resource name (e.g., "sessions/{session}/activities/{activity}").  |  
| `description`  |  `string` Output only. A description of this activity.  |  
| `createTime`  |  `string ( format)` Output only. The time at which this activity was created. Uses RFC 3339, where generated output will always be Z-normalized and use 0, 3, 6 or 9 fractional digits. Offsets other than "Z" are also accepted. Examples: `"2014-10-02T15:01:23Z"`, `"2014-10-02T15:01:23.045123456Z"` or `"2014-10-02T15:01:23+05:30"`.  |  
| `originator`  |  `string` The entity that this activity originated from (e.g. "user", "agent", "system").  |  
| `artifacts[]`  |  `object ()` Output only. The artifacts produced by this activity.  |  
| Union field `activity`. The activity content. `activity` can be only one of the following:  |  
| `agentMessaged`  |  `object ()` The agent posted a message.  |  
| `userMessaged`  |  `object ()` The user posted a message.  |  
| `planGenerated`  |  `object ()` A plan was generated.  |  
| `planApproved`  |  `object ()` A plan was approved.  |  
| `progressUpdated`  |  `object ()` There was a progress update.  |  
| `sessionCompleted`  |  `object ()` The session was completed.  |  
| `sessionFailed`  |  `object ()` The session failed.  |  
## AgentMessaged
The agent posted a message.  
| JSON representation  |  
| --- |  
| 
```
{
  "agentMessage": string
}
```
 |  
| Fields  |  
| --- |  
| `agentMessage`  |  `string` The message the agent posted.  |  
## UserMessaged
The user posted a message.  
| JSON representation  |  
| --- |  
| 
```
{
  "userMessage": string
}
```
 |  
| Fields  |  
| --- |  
| `userMessage`  |  `string` The message the user posted.  |  
## PlanGenerated
A plan was generated.  
| JSON representation  |  
| --- |  
| 
```
{
  "plan": {
    object ()
  }
}
```
 |  
| Fields  |  
| --- |  
| `plan`  |  `object ()` The plan that was generated.  |  
## Plan
A plan is a sequence of steps that the agent will take to complete the task.  
| JSON representation  |  
| --- |  
| 
```
{
  "id": string,
  "steps": [
    {
      object ()
    }
  ],
  "createTime": string
}
```
 |  
| Fields  |  
| --- |  
|  `string` Output only. ID for this plan; unique within a session.  |  
| `steps[]`  |  `object ()` Output only. The steps in the plan.  |  
| `createTime`  |  `string ( format)` Output only. Time when the plan was created. Uses RFC 3339, where generated output will always be Z-normalized and use 0, 3, 6 or 9 fractional digits. Offsets other than "Z" are also accepted. Examples: `"2014-10-02T15:01:23Z"`, `"2014-10-02T15:01:23.045123456Z"` or `"2014-10-02T15:01:23+05:30"`.  |  
## PlanStep
A step in a plan.  
| JSON representation  |  
| --- |  
| 
```
{
  "id": string,
  "title": string,
  "description": string,
  "index": integer
}
```
 |  
| Fields  |  
| --- |  
|  `string` Output only. ID for this step; unique within a plan.  |  
| `title`  |  `string` Output only. The title of the step.  |  
| `description`  |  `string` Output only. The description of the step.  |  
| `index`  |  `integer` Output only. 0-based index into the plan.steps.  |  
## PlanApproved
A plan was approved.  
| JSON representation  |  
| --- |  
| 
```
{
  "planId": string
}
```
 |  
| Fields  |  
| --- |  
| `planId`  |  `string` The ID of the plan that was approved.  |  
## ProgressUpdated
There was a progress update.  
| JSON representation  |  
| --- |  
| 
```
{
  "title": string,
  "description": string
}
```
 |  
| Fields  |  
| --- |  
| `title`  |  `string` The title of the progress update.  |  
| `description`  |  `string` The description of the progress update.  |  
## SessionCompleted
This type has no fields.
The session was completed.
## SessionFailed
The session failed.  
| JSON representation  |  
| --- |  
| 
```
{
  "reason": string
}
```
 |  
| Fields  |  
| --- |  
| `reason`  |  `string` The reason the session failed.  |  
## Artifact
An artifact is a single unit of data produced by an activity step.  
| JSON representation  |  
| --- |  
| 
```
{

  // Union field content can be only one of the following:
  "changeSet": {
    object ()
  },
  "media": {
    object ()
  },
  "bashOutput": {
    object ()
  }
  // End of list of possible types for union field content.
}
```
 |  
| Fields  |  
| --- |  
| Union field `content`. The artifact content. `content` can be only one of the following:  |  
| `changeSet`  |  `object ()` A change set was produced (e.g. code changes).  |  
| `media`  |  `object ()` A media file was produced (e.g. image, video).  |  
| `bashOutput`  |  `object ()` A bash output was produced.  |  
## ChangeSet
A set of changes to be applied to a source.  
| JSON representation  |  
| --- |  
| 
```
{
  "source": string,

  // Union field changes can be only one of the following:
  "gitPatch": {
    object ()
  }
  // End of list of possible types for union field changes.
}
```
 |  
| Fields  |  
| --- |  
| `source`  |  `string` The name of the source this change set applies to. Format: sources/{source}  |  
| Union field `changes`. The changes to be applied to the source. `changes` can be only one of the following:  |  
| `gitPatch`  |  `object ()` A patch in Git format.  |  
## GitPatch
A patch in Git format.  
| JSON representation  |  
| --- |  
| 
```
{
  "unidiffPatch": string,
  "baseCommitId": string,
  "suggestedCommitMessage": string
}
```
 |  
| Fields  |  
| --- |  
| `unidiffPatch`  |  `string` The patch in unidiff format.  |  
| `baseCommitId`  |  `string` The base commit id of the patch. This is the id of the commit that the patch should be applied to.  |  
| `suggestedCommitMessage`  |  `string` A suggested commit message for the patch, if one is generated.  |  
## Media
A media output.  
| JSON representation  |  
| --- |  
| 
```
{
  "data": string,
  "mimeType": string
}
```
 |  
| Fields  |  
| --- |  
| `data`  |  `string (bytes[](https://developers.google.com/discovery/v1/type-format) format)` The media data. A base64-encoded string.  |  
| `mimeType`  |  `string` The media mime type.  |  
## BashOutput
A bash output.  
| JSON representation  |  
| --- |  
| 
```
{
  "command": string,
  "output": string,
  "exitCode": integer
}
```
 |  
| Fields  |  
| --- |  
| `command`  |  `string` The bash command.  |  
| `output`  |  `string` The bash output. Includes both stdout and stderr.  |  
| `exitCode`  |  `integer` The bash exit code.  |  
| 
## Methods
 |  
| --- |  
|  Gets a single activity.  |  
|  Lists activities for a session.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-29 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/list
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/list#main-content)



Sign in
  * On this page




#  Method: sessions.activities.list Stay organized with collections  Save and categorize content based on your preferences.
  * On this page


  * [Path parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/list#body.PATH_PARAMETERS)
  * [Query parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/list#body.QUERY_PARAMETERS)
  * [Response body](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/list#body.response_body)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/list#body.ListActivitiesResponse.SCHEMA_REPRESENTATION)


Lists activities for a session.
### HTTP request
`GET https://jules.googleapis.com/v1alpha/{parent=sessions/*}/activities`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Path parameters  
| Parameters  |  
| --- |  
| `parent`  |  `string` Required. The parent session, which owns this collection of activities. Format: sessions/{session} It takes the form `sessions/{session}`.  |  
### Query parameters  
| Parameters  |  
| --- |  
| `pageSize`  |  `integer` Optional. The number of activities to return. Must be between 1 and 100, inclusive. If unset, defaults to 50. If set to greater than 100, it will be coerced to 100.  |  
| `pageToken`  |  `string` Optional. A page token, received from a previous `activities.list` call.  |  
### Request body
The request body must be empty.
### Response body
Response message for the activities.list RPC.
If successful, the response body contains data with the following structure:  
| JSON representation  |  
| --- |  
| 
```
{
  "activities": [
    {
      object ()
    }
  ],
  "nextPageToken": string
}
```
 |  
| Fields  |  
| --- |  
| `activities[]`  |  `object ()` The activities from the specified session.  |  
| `nextPageToken`  |  `string` A token, which can be sent as `pageToken` to retrieve the next page. If this field is omitted, there are no subsequent pages.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-11 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/get
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/get#main-content)



Sign in
  * On this page




#  Method: sessions.activities.get Stay organized with collections  Save and categorize content based on your preferences.
  * On this page


  * [Path parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions.activities/get#body.PATH_PARAMETERS)


Gets a single activity.
### HTTP request
`GET https://jules.googleapis.com/v1alpha/{name=sessions/*/activities/*}`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Path parameters  
| Parameters  |  
| --- |  
| `name`  |  `string` Required. The resource name of the activity to retrieve. Format: sessions/{session}/activities/{activity} It takes the form `sessions/{session}/activities/{activities}`.  |  
### Request body
The request body must be empty.
### Response body
If successful, the response body contains an instance of .
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-11 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/approvePlan
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/approvePlan#main-content)



Sign in
  * On this page




#  Method: sessions.approvePlan Stay organized with collections  Save and categorize content based on your preferences.
  * On this page


  * [Path parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/approvePlan#body.PATH_PARAMETERS)


Approves a plan in a session.
### HTTP request
`POST https://jules.googleapis.com/v1alpha/{session=sessions/*}:approvePlan`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Path parameters  
| Parameters  |  
| --- |  
| `session`  |  `string` Required. The resource name of the session to approve the plan in. Format: sessions/{session} It takes the form `sessions/{session}`.  |  
### Request body
The request body must be empty.
### Response body
If successful, the response body is empty.
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-29 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/create
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/create#main-content)



Sign in
  * On this page




#  Method: sessions.create Stay organized with collections  Save and categorize content based on your preferences.
  * On this page




Creates a new session.
### HTTP request
`POST https://jules.googleapis.com/v1alpha/sessions`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Request body
The request body contains an instance of .
### Response body
If successful, the response body contains a newly created instance of .
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-11 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/get
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/get#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  Method: sessions.get Stay organized with collections  Save and categorize content based on your preferences. 
  * [Path parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/get#body.PATH_PARAMETERS)


Gets a single session.
### HTTP request
`GET https://jules.googleapis.com/v1alpha/{name=sessions/*}`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Path parameters  
| Parameters  |  
| --- |  
| `name`  |  `string` Required. The resource name of the session to retrieve. Format: sessions/{session} It takes the form `sessions/{session}`.  |  
### Request body
The request body must be empty.
### Response body
If successful, the response body contains an instance of .
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-11 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/sendMessage
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/sendMessage#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  Method: sessions.sendMessage Stay organized with collections  Save and categorize content based on your preferences. 
  * [Path parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/sendMessage#body.PATH_PARAMETERS)
  * [Request body](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/sendMessage#body.request_body)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/sendMessage#body.request_body.SCHEMA_REPRESENTATION)


Sends a message from the user to a session.
### HTTP request
`POST https://jules.googleapis.com/v1alpha/{session=sessions/*}:sendMessage`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Path parameters  
| Parameters  |  
| --- |  
| `session`  |  `string` Required. The resource name of the session to post the message to. Format: sessions/{session} It takes the form `sessions/{session}`.  |  
### Request body
The request body contains data with the following structure:  
| JSON representation  |  
| --- |  
| 
```
{
  "prompt": string
}
```
 |  
| Fields  |  
| --- |  
| `prompt`  |  `string` Required. The user prompt to send to the session.  |  
### Response body
If successful, the response body is empty.
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-10-03 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sources
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  REST Resource: sources Stay organized with collections  Save and categorize content based on your preferences. 
  * [Resource: Source](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#Source)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#Source.SCHEMA_REPRESENTATION)
  * [GitHubRepo](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#GitHubRepo)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#GitHubRepo.SCHEMA_REPRESENTATION)
  * [GitHubBranch](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#GitHubBranch)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sources#GitHubBranch.SCHEMA_REPRESENTATION)


## Resource: Source
An input source of data for a session.  
| JSON representation  |  
| --- |  
| 
```
{
  "name": string,
  "id": string,

  // Union field source can be only one of the following:
  "githubRepo": {
    object ()
  }
  // End of list of possible types for union field source.
}
```
 |  
| Fields  |  
| --- |  
| `name`  |  `string` Identifier. The full resource name (e.g., "sources/{source}").  |  
|  `string` Output only. The id of the source. This is the same as the "{source}" part of the resource name (e.g., "sources/{source}").  |  
| Union field `source`. The input data source. `source` can be only one of the following:  |  
| `githubRepo`  |  `object ()` A GitHub repo.  |  
## GitHubRepo
A GitHub repo.  
| JSON representation  |  
| --- |  
| 
```
{
  "owner": string,
  "repo": string,
  "isPrivate": boolean,
  "defaultBranch": {
    object ()
  },
  "branches": [
    {
      object ()
    }
  ]
}
```
 |  
| Fields  |  
| --- |  
| `owner`  |  `string` The owner of the repo; the `<owner>` in `https://github.com/<owner>/<repo>`.  |  
| `repo`  |  `string` The name of the repo; the `<repo>` in `https://github.com/<owner>/<repo>`.  |  
| `isPrivate`  |  `boolean` Whether this repo is private.  |  
| `defaultBranch`  |  `object ()` The default branch for this repo.  |  
| `branches[]`  |  `object ()` The list of active branches for this repo.  |  
## GitHubBranch
A GitHub branch.  
| JSON representation  |  
| --- |  
| 
```
{
  "displayName": string
}
```
 |  
| Fields  |  
| --- |  
| `displayName`  |  `string` The name of the GitHub branch.  |  
| 
## Methods
 |  
| --- |  
|  Gets a single source.  |  
|  Lists sources.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-29 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/list
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/list#main-content)



Sign in
  * On this page




#  Method: sessions.list Stay organized with collections  Save and categorize content based on your preferences.
  * On this page


  * [Query parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/list#body.QUERY_PARAMETERS)
  * [Response body](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/list#body.response_body)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sessions/list#body.ListSessionsResponse.SCHEMA_REPRESENTATION)


Lists all sessions.
### HTTP request
`GET https://jules.googleapis.com/v1alpha/sessions`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Query parameters  
| Parameters  |  
| --- |  
| `pageSize`  |  `integer` Optional. The number of sessions to return. Must be between 1 and 100, inclusive. If unset, defaults to 30. If set to greater than 100, it will be coerced to 100.  |  
| `pageToken`  |  `string` Optional. A page token, received from a previous `sessions.list` call.  |  
### Request body
The request body must be empty.
### Response body
Response message for sessions.list.
If successful, the response body contains data with the following structure:  
| JSON representation  |  
| --- |  
| 
```
{
  "sessions": [
    {
      object ()
    }
  ],
  "nextPageToken": string
}
```
 |  
| Fields  |  
| --- |  
| `sessions[]`  |  `object ()` The sessions from the specified request.  |  
| `nextPageToken`  |  `string` A token, which can be sent as `pageToken` to retrieve the next page. If this field is omitted, there are no subsequent pages.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-11 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sources/get
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sources/get#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  Method: sources.get Stay organized with collections  Save and categorize content based on your preferences. 
  * [Path parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sources/get#body.PATH_PARAMETERS)


Gets a single source.
### HTTP request
`GET https://jules.googleapis.com/v1alpha/{name=sources/**}`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Path parameters  
| Parameters  |  
| --- |  
| `name`  |  `string` Required. The resource name of the source to retrieve. Format: sources/{source} It takes the form `sources/{+source}`.  |  
### Request body
The request body must be empty.
### Response body
If successful, the response body contains an instance of .
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-30 UTC.


============================================================
# https://developers.google.com/jules/api/reference/rest/v1alpha/sources/list
============================================================

[ Skip to main content ](https://developers.google.com/jules/api/reference/rest/v1alpha/sources/list#main-content)


  * English
  * Deutsch
  * Español
  * Français
  * Indonesia
  * Português – Brasil
  * Русский
  * 中文 – 简体

Sign in


#  Method: sources.list Stay organized with collections  Save and categorize content based on your preferences. 
  * [Query parameters](https://developers.google.com/jules/api/reference/rest/v1alpha/sources/list#body.QUERY_PARAMETERS)
  * [Response body](https://developers.google.com/jules/api/reference/rest/v1alpha/sources/list#body.response_body)
    * [JSON representation](https://developers.google.com/jules/api/reference/rest/v1alpha/sources/list#body.ListSourcesResponse.SCHEMA_REPRESENTATION)


Lists sources.
### HTTP request
`GET https://jules.googleapis.com/v1alpha/sources`
The URL uses [gRPC Transcoding](https://google.aip.dev/127) syntax.
### Query parameters  
| Parameters  |  
| --- |  
| `filter`  |  `string` Optional. The filter expression for listing sources, based on AIP-160. If not set, all sources will be returned. Currently only supports filtering by name, which can be used to filter by a single source or multiple sources separated by OR. Example filters: - 'name=sources/source1 OR name=sources/source2'  |  
| `pageSize`  |  `integer` Optional. The number of sources to return. Must be between 1 and 100, inclusive. If unset, defaults to 30. If set to greater than 100, it will be coerced to 100.  |  
| `pageToken`  |  `string` Optional. A page token, received from a previous `sources.list` call.  |  
### Request body
The request body must be empty.
### Response body
Response message for the sources.list RPC.
If successful, the response body contains data with the following structure:  
| JSON representation  |  
| --- |  
| 
```
{
  "sources": [
    {
      object ()
    }
  ],
  "nextPageToken": string
}
```
 |  
| Fields  |  
| --- |  
| `sources[]`  |  `object ()` The sources from the specified request.  |  
| `nextPageToken`  |  `string` A token, which can be sent as `pageToken` to retrieve the next page. If this field is omitted, there are no subsequent pages.  |  
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-09-11 UTC.


============================================================
# https://developers.google.com/products
============================================================

[ Skip to main content ](https://developers.google.com/products#main-content)
  * [Español – América Latina](https://developers.google.com/products?hl=es-419)
  * [Português – Brasil](https://developers.google.com/products?hl=pt-br)

Sign in


# Developer products
Explore our suite of developer products designed to fuel your innovation, streamline development, and unlock new features and growth for your projects. 
[ Android Modern tools to help you build experiences that people love across every Android device. ](https://developer.android.com)
[ Google Cloud Build apps faster, make smarter business decisions, and connect people everywhere. ](https://console.cloud.google.com/freetrial?redirectPath=/products/solutions/catalog&utm_source=developers.google.com&utm_medium=et&utm_campaign=FY24-Q1-DGC-HP-Google-Cloud-card)
[ Google AI Studio Build generative AI applications quickly with Gemini in Google AI Studio. ](https://aistudio.google.com/app/prompts/new_chat/?utm_source=gfd&utm_medium=referral&utm_campaign=home_garden&utm_content=)
[ Chrome Modern tools and features that help you build high-quality web experiences. ](https://developer.chrome.com/)
filter_listFilters


============================================================
# https://developers.google.com/site-policies
============================================================

[ Skip to main content ](https://developers.google.com/terms/site-policies#main-content)
  * [Español – América Latina](https://developers.google.com/terms/site-policies?hl=es-419)

Sign in
  * On this page


#  Site Policies Stay organized with collections  Save and categorize content based on your preferences.
  * On this page


## Page Summary
outlined_flag
  * Google Developers documentation is largely licensed under Creative Commons Attribution 4.0, allowing reuse and modification with attribution.
  * You can use content for various purposes, like quoting in books or translating, as long as Google is credited.
  * Google's trademarks and brand features are excluded from this license; refer to their brand usage guidelines.
  * Content like images, audio, video, or external links may have separate licensing and might not be covered.
  * Proper attribution is essential and should include a statement and link back to the original Google Developers page.


We are pleased to license much of the documentation on Google Developers under terms that explicitly encourage people to take, modify, reuse, re-purpose, and remix our work as they see fit. 
You will find the following notice at the bottom of many pages on the Google Developers website: 
> Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/). For details, see our [Site Policies](https://developers.google.com/readme/policies).
When you see a page with this notice you are free to use [nearly everything](https://developers.google.com/terms/site-policies#restrictions) on the page in your own creations. For example, you could quote the text in a book, cut-and-paste sections to your blog, record it as an audiobook for the visually impaired, or even translate it into Swahili. Really. That's what open content licenses are all about. We just ask that you give us [attribution](https://developers.google.com/terms/site-policies#attribution) when you reuse our work. 
You may also find the following notice on the bottom of some pages:
> Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see our [Site Policies](https://developers.google.com/readme/policies).
When you see this notice, you are free to use the content, and in addition you are free to use the computer source code that appears in the content (such as in examples) in the code of your own projects. 
## What is _not_ licensed?
We say "nearly everything" as there are a few simple conditions that apply. 
Google's trademarks and other brand features are not included in this license. Please see our [standard guidelines for third-party use of Google brand features](https://www.google.com/permissions/ "Google Permissions & Guidelines") for information about this usage. 
In some cases, a page may include content consisting of images, audio or video material, or a link to content on a different webpage (such as videos or slide decks). This content is not covered by the license, unless specifically noted. 
## Attribution
Proper attribution is required when you reuse or create modified versions of content that appears on a page made available under the terms of the Creative Commons Attribution license. The complete requirements for attribution can be found in section 3 of the [Creative Commons legal code](https://creativecommons.org/licenses/by/4.0/legalcode). 
In practice we ask that you provide attribution to Google to the best of the ability of the medium in which you are producing the work. 
There are several typical ways in which this might apply: 
#### Exact Reproductions
If your online work _exactly reproduces_ text or images from this site, in whole or in part, please include a paragraph at the bottom of your page that reads: 
> Portions of this page are reproduced from work created and [shared by Google](https://developers.google.com/readme/policies) and used according to terms described in the [Creative Commons 4.0 Attribution License](https://creativecommons.org/licenses/by/4.0/). 
Also, please link back to the original source page so that readers can refer to it for more information. 
#### Modified Versions
If your online work shows _modified_ text or images based on the content from this site, please include a paragraph at the bottom of your page that reads: 
> Portions of this page are modifications based on work created and [shared by Google](https://developers.google.com/readme/policies) and used according to terms described in the [Creative Commons 4.0 Attribution License](https://creativecommons.org/licenses/by/4.0/). 
Again, please link back to the original source page so that readers can refer to it for more information. This is even more important when the content has been modified. 
#### Other Media
If you produce non-hypertext works, such as books, audio, or video, we ask that you make a best effort to include a spoken or written attribution in the spirit of the messages above. 
Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2025-08-06 UTC.
