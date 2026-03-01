from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import OrgNode
from .serializers import OrgNodeSerializer
from .permissions import IsHierarchicalSuperior

class OrgNodeViewSet(viewsets.ModelViewSet):
    serializer_class = OrgNodeSerializer
    # Standard permission for viewing data
    permission_classes = [IsAuthenticated, IsHierarchicalSuperior]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'org_node'):
            from .tasks import get_subtree_ids
            ids = get_subtree_ids(user.org_node.id)
            return OrgNode.objects.filter(id__in=ids)
        return OrgNode.objects.none()

    # --- THE NEW PROMOTION ENDPOINT ---
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def replace_employee(self, request, pk=None):
        """
        POST /api/nodes/{old_ceo_id}/replace_employee/
        Body: { "replacement_id": 5 } 
        
        Logic:
        1. 'pk' is the OLD person (A) to be fired.
        2. 'replacement_id' is the NEW person (B or C) taking the job.
        3. B inherits A's job title and A's subordinates.
        4. A is deleted (and their personal data cascades away).
        """
        old_node_id = pk
        new_node_id = request.data.get('replacement_id')

        if not new_node_id:
            return Response({"error": "replacement_id is required"}, status=400)

        try:
            with transaction.atomic(): # Ensure all steps happen or none happen
                old_node = OrgNode.objects.get(id=old_node_id)
                new_node = OrgNode.objects.get(id=new_node_id)

                # Step 1: Validate Company Match
                if old_node.company_id != new_node.company_id:
                    return Response({"error": "Cannot cross-promote between companies"}, status=400)

                # Step 2: "Inheritance" - New Node takes Old Node's Place
                # A. Take the Title
                new_node.structure_level = old_node.structure_level
                
                # B. Take the Boss (If Old Node was CEO, Boss is None)
                # Important: If promoting internally (C replacing A), ensure we don't set C.parent = C
                if old_node.parent_id == new_node.id:
                    # If C was child of A, C's new parent should be A's parent
                    new_node.parent = old_node.parent 
                else:
                    new_node.parent = old_node.parent

                new_node.save()

                # Step 3: "Adoption" - Move Old Node's children to New Node
                # We update all children of A to now report to B
                # We exclude B itself from this update to avoid a self-loop
                old_node.children.exclude(id=new_node.id).update(parent=new_node)

                # Step 4: Fire the Old Node
                # Because PerformanceMetric uses CASCADE, this wipes A's history.
                # Because OrgNode uses SET_NULL (children), the children are safe 
                # (they were already moved in Step 3 anyway).
                old_node.delete()

                return Response({
                    "message": f"{old_node.name} removed. {new_node.name} is now {new_node.structure_level.name}."
                })

        except OrgNode.DoesNotExist:
            return Response({"error": "Node not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)