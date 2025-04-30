$(document).ready(function() {
    const chatBody = $("#chatBody");
    const chatInput = $("#chatInput");
    const repoUrl = $("#repoUrl");
    const repoSubmitButton = $("#repoSubmitButton");
    const loadingSpinner = $("#loadingSpinner");
    const clearButton = $("#clearButton");
    const clearChatButton = $("#clearChatButton");
    const currentRepoInfo = $("#currentRepoInfo");
    const repoNameSpan = $("#repoName");

    // Function to update current repository info
    function updateCurrentRepo() {
        $.ajax({
            type: "GET",
            url: "/get_current_repo",
            timeout: 30000
        })
        .done(function(response) {
            if (response.repo_name) {
                $("#repoName").text(response.repo_name);
                $("#currentRepoInfo").removeClass('d-none');
            } else {
                $("#currentRepoInfo").addClass('d-none');
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.error("Error getting repo info:", textStatus, errorThrown);
            $("#currentRepoInfo").addClass('d-none');
        });
    }

    // Call on page load
    updateCurrentRepo();

    // Utility functions
    function getCurrentTime() {
        return new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    function scrollToBottom() {
        chatBody.scrollTop(chatBody[0].scrollHeight);
    }

    function addMessage(content, isUser = false) {
        if (!content) return;
        
        const messageHtml = `
            <div class="d-flex justify-content-${isUser ? 'end' : 'start'}">
                <div class="message ${isUser ? 'user-message' : 'bot-message'}">
                    <div class="message-content">${content}</div>
                    <span class="timestamp">${getCurrentTime()}</span>
                </div>
            </div>
        `;
        chatBody.append(messageHtml);
        scrollToBottom();
    }

    function setLoading(isLoading) {
        repoSubmitButton.prop('disabled', isLoading);
        clearButton.prop('disabled', isLoading);
        repoSubmitButton.text(isLoading ? 'Analyzing...' : 'Analyze Repository');
        loadingSpinner.toggleClass('d-none', !isLoading);
    }

    function clearChat() {
        chatBody.empty();
        addMessage(`Hello! 👋 Please analyze a repository first, then I'll be happy to answer any questions about the code! 🚀`);
    }

    // Initial welcome message
    addMessage(`Hello! 👋 Please analyze a repository first, then I'll be happy to answer any questions about the code! 🚀`);

    // Handle chat form submission
    $("#chatForm").on("submit", function(event) {
        event.preventDefault();
        const message = chatInput.val().trim();
        
        if (!message) return;

        addMessage(message, true);
        chatInput.val('').prop('disabled', true);

        $.ajax({
            data: { msg: message },
            type: "POST",
            url: "/get",
            timeout: 30000, // 30 second timeout
        })
        .done(function(response) {
            if (response.error) {
                addMessage("Error: " + response.error);
            } else if (response.answer) {
                addMessage(response.answer);
            } else {
                addMessage("Received an invalid response from the server");
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            addMessage("Sorry, I encountered an error. Please try again.");
            console.error("Chat error:", textStatus, errorThrown);
        })
        .always(function() {
            chatInput.prop('disabled', false).focus();
        });
    });

    // Handle repository form submission
    $("#repoForm").on("submit", function(e) {
        e.preventDefault();
        const repoUrlValue = repoUrl.val().trim();
        
        if (!repoUrlValue.startsWith('https://github.com/')) {
            alert('Please enter a valid GitHub repository URL');
            return;
        }

        setLoading(true);
        
        $.ajax({
            data: { question: repoUrlValue },
            type: "POST",
            url: "/chatbot",
            timeout: 60000, // 60 second timeout
        })
        .done(function(response) {
            const repoName = response.repo_name || repoUrlValue.split('/').pop().replace('.git', '');
            addMessage(`Repository "${repoName}" has been successfully analyzed. You can now ask questions about the code!`);
            repoUrl.val('');
            updateCurrentRepo();
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            addMessage("Error: Failed to process repository. Please try again.");
            console.error("Error:", jqXHR.responseText);
        })
        .always(function() {
            setLoading(false);
        });
    });

    // Handle clear button click
    clearButton.on("click", function() {
        if (confirm("Are you sure you want to clear the current repository? This will remove all analysis data.")) {
            $.ajax({
                type: "POST",
                url: "/clear_cache",
                timeout: 30000
            })
            .done(function(response) {
                clearChat();
                repoUrl.val('');
                chatInput.val('');
                currentRepoInfo.addClass('d-none');
                alert("Repository cleared successfully!");
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                console.error("Clear cache error:", textStatus, errorThrown);
                alert("Failed to clear repository. Please try again.");
            });
        }
    });

    // Handle clear chat button click
    clearChatButton.on("click", function() {
        if (confirm("Are you sure you want to clear the chat history?")) {
            clearChat();
        }
    });
});
