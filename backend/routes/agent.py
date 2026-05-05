from flask import Blueprint, request, jsonify, session, render_template
from flask_login import current_user, login_required
from ..models import Agent
from ..extensions import db
import requests

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/', methods=['GET'])
@login_required
def get_agents():
    agents = Agent.query.all()
    return jsonify([
        {
            'id': agent.id,
            'name': agent.name,
            'description': agent.description,
            'status': agent.status,
            'capabilities': agent.capabilities
        }
        for agent in agents
    ])

@agent_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_agent(id):
    agent = Agent.query.get_or_404(id)
    return jsonify({
        'id': agent.id,
        'name': agent.name,
        'description': agent.description,
        'status': agent.status,
        'endpoint_url': agent.endpoint_url,
        'capabilities': agent.capabilities
    })

@agent_bp.route('/<int:id>/execute', methods=['POST'])
@login_required
def execute_capability(id):
    agent = Agent.query.get_or_404(id)
    
    if agent.status != 'active':
        return jsonify({'error': f'Agent is not active (status: {agent.status})'}), 400
    
    data = request.get_json()
    capability_name = data.get('capability')
    params = data.get('params', {})
    
    if not capability_name:
        return jsonify({'error': 'Capability name required'}), 400
    
    # Forward request to external agent API
    try:
        response = requests.post(
            f"{agent.endpoint_url}/{capability_name}",
            json=params,
            timeout=30
        )
        
        return jsonify(response.json())
        
    except requests.Timeout:
        return jsonify({'error': 'Agent API timeout'}), 504
    except requests.ConnectionError:
        return jsonify({'error': 'Could not connect to agent API'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/', methods=['POST'])
@login_required
def create_agent():
    data = request.get_json()
    
    if not all([data.get('name'), data.get('endpoint_url')]):
        return jsonify({'error': 'Name and endpoint_url required'}), 400
    
    agent = Agent(
        name=data['name'],
        description=data.get('description', ''),
        endpoint_url=data['endpoint_url'],
        status=data.get('status', 'active'),
        capabilities=data.get('capabilities', [])
    )
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'agent': {
            'id': agent.id,
            'name': agent.name
        }
    }), 201
