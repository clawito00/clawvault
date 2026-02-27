#!/bin/bash
# Bash completion for clawvault

_clawvault_completion() {
    local cur prev words cword
    _init_completion || return

    # Commands that require service name completion
    local service_cmds="get update delete"

    # Get the command being used
    local cmd="${words[1]}"

    # If completing the command itself
    if [[ ${cword} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "add get list search update delete passwd backup backups restore export import --help" -- "${cur}"))
        return
    fi

    # If completing a service name for get/update/delete
    if [[ ${service_cmds} == *"${cmd}"* ]] && [[ ${cword} -eq 2 ]] && [[ ${prev} != "--tag" ]] && [[ ${prev} != "-t" ]]; then
        # Get list of services from vault (requires password, so we show common patterns)
        # Note: In practice, users would need to unlock vault first
        # This provides a hint about the format
        COMPREPLY=($(compgen -W "github openai stripe aws anthropic" -- "${cur}"))
        return
    fi

    # Options for specific commands
    case "${cmd}" in
        add)
            if [[ ${prev} == "--tag" ]] || [[ ${prev} == "-t" ]]; then
                COMPREPLY=($(compgen -W "api production development staging test" -- "${cur}"))
                return
            fi
            COMPREPLY=($(compgen -W "--key --tag -k -t --help" -- "${cur}"))
            ;;
        get)
            COMPREPLY=($(compgen -W "--copy -c --help" -- "${cur}"))
            ;;
        list)
            if [[ ${prev} == "--tag" ]] || [[ ${prev} == "-t" ]]; then
                COMPREPLY=($(compgen -W "api production development staging test" -- "${cur}"))
                return
            fi
            COMPREPLY=($(compgen -W "--tag --verbose -t -v --help" -- "${cur}"))
            ;;
        update)
            if [[ ${prev} == "--tag" ]] || [[ ${prev} == "-t" ]]; then
                COMPREPLY=($(compgen -W "api production development staging test" -- "${cur}"))
                return
            fi
            COMPREPLY=($(compgen -W "--key --tag -k -t --help" -- "${cur}"))
            ;;
        delete)
            COMPREPLY=($(compgen -W "--force -f --help" -- "${cur}"))
            ;;
        export)
            COMPREPLY=($(compgen -W "--encrypt -e --help" -- "${cur}"))
            ;;
        import)
            COMPREPLY=($(compgen -W "--decrypt -d --help" -- "${cur}"))
            ;;
        restore)
            # File completion
            COMPREPLY=($(compgen -f -- "${cur}"))
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -F _clawvault_completion clawvault
